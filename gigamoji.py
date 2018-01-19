from flask import Flask, Response, Request, request

from slackclient import SlackClient

import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

import os, json, requests, re

# 認証情報は環境変数に置く
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_CLIENT_ID = os.environ["SLACK_CLIENT_ID"]
SLACK_CLIENT_SECRET = os.environ["SLACK_CLIENT_SECRET"]
AWS_REGION = os.environ["AWS_REGION"]
DYNAMODB_TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]

# Flask, DynamoDB
app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def die_noretry(code):
    # X-Slack-No-Retry をヘッダに設定して，エラー時のリトライを無効化
    return Response(headers={"X-Slack-No-Retry": 1}, status=code)

def challenge_response(data):
    return Response(data['challenge'], mimetype='application/x-www-form-urlencoded', status=200)

def event_callback(data):
    data = request.get_json()
    retry_num = request.headers.get('X-Slack-Retry-Num')
    if retry_num and int(retry_num) > 0:
        return die_noretry(200)

    # messageイベントで，かつメッセージの削除・編集等ではないことを確認
    if data["event"]["type"] != "message" or "subtype" in data["event"]:
        print("event type mismatch")
        return die_noretry(400) # Bad Request

    team_id = data["team_id"]
    user_id = data["event"]["user"]

    # メッセージのテキストを取得，絵文字を切り出す
    message = data["event"]
    emoji_re = ':[a-z0-9\-_]+:'
    emoji_in_text = re.findall(emoji_re, message["text"])
    rest_text = re.sub(emoji_re, '', message["text"]) # 残りのテキスト

    # メッセージの中身が絵文字だけかの判定
    if len(emoji_in_text) != 1 or (rest_text and not rest_text.isspace()):
        print("emoji condition not met")
        return die_noretry(400) # Bad Request

    # ユーザのトークンをDynamoDBテーブルから取得
    response = table.get_item(Key={'TeamUserId': team_id+user_id})
    # Slackクライアントを生成
    slack_client = SlackClient(response['Item']["UserToken"])

    # 絵文字の画像URLを取得
    emoji_list_response = slack_client.api_call("emoji.list")
    emoji_name = emoji_in_text[0].strip(":")
    emoji_url = emoji_list_response["emoji"].get(emoji_name)
    if emoji_url is None:
        print("emoji url is not set")
        return die_noretry(400)

    # もとのメッセージを消して，スタンプ化した絵文字を投稿する
    channel = message["channel"]
    att = [{ "fallback": "スタンプを送信しました", "image_url": emoji_url }]
    slack_client.api_call("chat.delete", channel=channel, ts=message["ts"], as_user=True)
    slack_client.api_call("chat.postMessage", channel=channel, text="", attachments=json.dumps(att), as_user=True)

    return Response("")

@app.route("/", methods=['POST'])
def root():
    data = request.get_json()

    # このリクエストがSlackからきたものかどうかを簡易的に判定
    if ('type' not in data) or ('token' not in data) or (data['token'] != SLACK_VERIFICATION_TOKEN) :
        return die_noretry(400)

    if data['type'] == 'url_verification':
        return challenge_response(data)
    if data['type'] == 'event_callback':
        return event_callback(data)

@app.route("/", methods=['GET'])
def pre_auth():
    add_to_slack = """
        <a href="https://slack.com/oauth/authorize?&client_id=%s&scope=chat:write:user,emoji:read,channels:history,groups:history,im:history,mpim:history">
            <img alt="Add to Slack" src="https://platform.slack-edge.com/img/add_to_slack.png"/>
        </a>
    """ % SLACK_CLIENT_ID
    return add_to_slack

@app.route("/auth_callback", methods=["GET"])
def auth_callback():
    # OAuthコードの取得
    auth_code = request.args.get('code')

    # OAuth認証のための一時的なSlackクライアントの生成(トークン必要なし)
    slack_client = SlackClient("")

    # OAuth認証し，ユーザトークンを取得
    auth_response = slack_client.api_call("oauth.access", client_id=SLACK_CLIENT_ID, client_secret=SLACK_CLIENT_SECRET, code=auth_code)
    user_token = auth_response.get("access_token")

    # ユーザに紐付いたSlackクライアントの生成
    slack_client = SlackClient(user_token)
    # チーム名，チームIDとユーザIDを取得
    response = slack_client.api_call("auth.test", token=user_token)
    team_name = response.get("team")
    team_id = response.get("team_id")
    user_id = response.get("user_id")

    # 古いアイテムは消しておく．ユーザトークンをDynamoDBに登録
    table.delete_item(Key={'TeamUserId': team_id+user_id})
    table.put_item(Item={'TeamUserId': team_id+user_id, 'UserToken': user_token})

    return "Gigamojiを<b>%s</b>にインストールしました!!" % (team_name)

@app.errorhandler(500)
def internal_server_error(error):
    return die_noretry(500)

if __name__ == "__main__":
    app.run()

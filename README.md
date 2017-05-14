# zappa-slack-gigamoji
**Make jumbomoji even BIGGER!**

Slackのカスタム絵文字をスタンプ風に表示させるSlack Appです．
Jumbomojiよりさらに大きくできます．

![スタンプ化されます](http://blog.tokor.org/2017/05/14/Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた/slack_stamp_anime.gif)

記事: [Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた | Tokoro's Tech-Note](http://blog.tokor.org/2017/05/14/Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた/)

## 特徴

* Slack Appなので全プラットフォームに対応
* 画像以外の余分なものをなるべく表示しない
* カスタム絵文字の追加だけでスタンプを追加できる
* モバイル端末に「スタンプを送信しました」の通知が届く

## 使用ソフトウェア

* virtualenv 15.1.0
* Python 3.6.1
   * zappa 0.41.2
   * Flask 0.12.1
   * slackclient 1.0.5

## 事前準備

* AWSのアカウント作成
* IAMコンソールで認証情報の作成
* AWS CLI等で認証情報ファイルの作成
* [Slack APIの設定(Step 1~4)](http://blog.tokor.org/2017/05/14/Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた/#Step1.SlackAppの登録)
* [DynamoDBでテーブル作成(Step 4)](http://blog.tokor.org/2017/05/14/Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた/#Step4.OAuth認証・DynamoDBへのユーザトークンの保存)

## セットアップ

1. virtualenvの作成とソフトウェア類のセットアップをします
   ```
   $ virtualenv env
   $ source env/bin/activate
   $ pip install flask zappa slackclient
   $ zappa init
   ```
1. [リモート環境変数ファイルをS3 Bucketにアップロードします(Step 7)](http://blog.tokor.org/2017/05/14/Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた/#Step7.zappaでのリモート環境変数の設定，デプロイ)
1. [`zappa_settings.json` を編集します(Step 7)](http://blog.tokor.org/2017/05/14/Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた/#Step7.zappaでのリモート環境変数の設定，デプロイ)
1. デプロイします
   ```
   $ zappa deploy environment名
   ```
1. 表示されたURLにアクセスしてAppを承認します
1. Slackで絵文字だけの投稿を行うと，スタンプ化されます  
   ![スタンプ化されます](http://blog.tokor.org/2017/05/14/Slackの絵文字をしっかりLINEスタンプ風にするAppを書いた/slack_stamp_anime.gif)

## MIT Open Source License

Copyright 2017 Tokoro

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

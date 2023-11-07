from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import random
import os
import openai
from firebase import firebase

import requests, json


app = Flask(__name__)

url = os.environ['firebaseurl']
fdb = firebase.FirebaseApplication(url, None)    # 初始化，第二個參數作用在負責使用者登入資訊，通常設定為 None
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    UserName = event.source.user_id
    username = line_bot_api.get_profile(UserName)
    if event.source.type == 'group':
        dataid = event.source.group_id
        fdb.put('/'+dataid,'test',1)
        if event.message.text[:2] == '訂貨':
            fdb.put('/'+dataid+'/A','店家','測試')
            fdb.put('/'+dataid+'/A','貨物','風熱友')
            fdb.put('/'+dataid+'/A','數量','50')
        
    
    else:
        print("test")
        
        UserName = event.source.user_id
        username = line_bot_api.get_profile(UserName)
        message = TextSendMessage(text= 'Hello '+username.display_name +' 小幫手目前的功能都是群組限定，若需小幫手幫助您整理貨單，請將小幫手與您的共事夥伴加入同一個群組呦！')
        line_bot_api.reply_message(event.reply_token, message)
                


        

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


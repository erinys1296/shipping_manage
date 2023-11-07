from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import random
import os
import openai
from firebase import firebase

import requests, json

url = 'https://line-notify-a56be-default-rtdb.firebaseio.com/'
fdb = firebase.FirebaseApplication(url, None)    # 初始化，第二個參數作用在負責使用者登入資訊，通常設定為 None
headers = {'Authorization':'Bearer '+os.environ['CHANNEL_ACCESS_TOKEN'],'Content-Type':'application/json'}
app = Flask(__name__)


line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
audiogame = {'B':'https://firebasestorage.googleapis.com/v0/b/line-notify-a56be.appspot.com/o/B.m4a?alt=media&token=d2d1fb7e-43b2-4349-bab7-925245ff301b&_gl=1*1knynyj*_ga*NjEwMjI3NzkzLjE2OTkwNjM3NDU.*_ga_CW55HF8NVT*MTY5OTI2Njg4OC40LjEuMTY5OTI2NzgyOS40NC4wLjA.',
            'C':'https://firebasestorage.googleapis.com/v0/b/line-notify-a56be.appspot.com/o/C.m4a?alt=media&token=b40c4926-b1c9-45f4-9dd0-24e05303e736&_gl=1*welz0v*_ga*NjEwMjI3NzkzLjE2OTkwNjM3NDU.*_ga_CW55HF8NVT*MTY5OTI2Njg4OC40LjEuMTY5OTI2Nzg2Ny42LjAuMA..',
            'D':'https://firebasestorage.googleapis.com/v0/b/line-notify-a56be.appspot.com/o/D.m4a?alt=media&token=370831c8-8217-4f34-845e-7b81d680d5c0&_gl=1*1lmu51g*_ga*NjEwMjI3NzkzLjE2OTkwNjM3NDU.*_ga_CW55HF8NVT*MTY5OTI3Nzk3MC41LjEuMTY5OTI3Nzk3MS41OS4wLjA.',
            'E':'https://firebasestorage.googleapis.com/v0/b/line-notify-a56be.appspot.com/o/E.m4a?alt=media&token=4d883570-f011-498a-be70-0ffdbb54cff4&_gl=1*wlzbd0*_ga*NjEwMjI3NzkzLjE2OTkwNjM3NDU.*_ga_CW55HF8NVT*MTY5OTI3Nzk3MC41LjEuMTY5OTI3ODAyOS4xLjAuMA..',
            'F':'https://firebasestorage.googleapis.com/v0/b/line-notify-a56be.appspot.com/o/F.m4a?alt=media&token=fa3225aa-c1af-4c76-8245-74656f178817&_gl=1*1mqwmzc*_ga*NjEwMjI3NzkzLjE2OTkwNjM3NDU.*_ga_CW55HF8NVT*MTY5OTI3Nzk3MC41LjEuMTY5OTI3ODA4OS44LjAuMA..',
            'G':'https://firebasestorage.googleapis.com/v0/b/line-notify-a56be.appspot.com/o/G.m4a?alt=media&token=cf0c7a78-e611-49a0-ae4a-7b2a9fbe9d6e&_gl=1*k9s81d*_ga*NjEwMjI3NzkzLjE2OTkwNjM3NDU.*_ga_CW55HF8NVT*MTY5OTI3Nzk3MC41LjEuMTY5OTI3ODEwNC41OS4wLjA.'}


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
    else:
        
        dataid = username.user_id
    try: 
        test = fdb.get('/'+dataid,'start')
    except:
        fdb.put('/'+dataid,'start',0)
        
    try: 
        test = fdb.get('/'+dataid,'startaudio')
    except:
        fdb.put('/'+dataid,'startaudio',0)
        
    if event.message.text == '開始猜數字':
        answer = random.randint(2,99)
        message = TextSendMessage(text="請從1到100中猜個數字 " )
        line_bot_api.reply_message(event.reply_token, message)
        counter = 0
        fdb.put('/'+dataid,'start',1)
        fdb.put('/'+dataid,'min',1)
        fdb.put('/'+dataid,'max',100)
        fdb.put('/'+dataid,'count',0)
        fdb.put('/'+dataid,'answer',answer)
    elif event.message.text == '開始猜音':
        answers = ['B','C','D','E','F','G']
        answer = answers[random.randint(0,5)]
        fdb.put('/'+dataid,'startaudio',1)
        fdb.put('/'+dataid,'audioanswer',answer)
        message = TextSendMessage(text="先給一個A" )
        line_bot_api.reply_message(event.reply_token, message)
        body = {
        'to':username.user_id,
        'messages':[{
                "type": "audio",
                "originalContentUrl": "https://firebasestorage.googleapis.com/v0/b/line-notify-a56be.appspot.com/o/A.m4a?alt=media&token=ef2f2ff9-cd1c-48d7-a7f2-7e6746263844&_gl=1*l97xkq*_ga*NjEwMjI3NzkzLjE2OTkwNjM3NDU.*_ga_CW55HF8NVT*MTY5OTI2Njg4OC40LjEuMTY5OTI2NzA4Ny4xMC4wLjA.",
                "duration": 2000
            }]
        }
        req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))

        body = {
        'to':username.user_id,
        'messages':[{
                "type": "text",
                "text":"猜猜這是什麼音"
            }]
        }
        req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
       
        body = {
        'to':username.user_id,
        'messages':[{
                "type": "audio",
                "originalContentUrl": audiogame[answer],
                "duration": 2000
            }]
        }
        req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
       
        
    elif fdb.get('/'+dataid,'start') == 1:
        count = fdb.get('/'+dataid,'count') + 1
        fdb.put('/'+dataid,'count',count)
        min = fdb.get('/'+dataid,'min')
        max = fdb.get('/'+dataid,'max')
        if event.message.text == "結束":
            message = TextSendMessage(text= "遊戲已終止，想再玩一次請輸入「開始猜數字」" )
            line_bot_api.reply_message(event.reply_token, message)
            fdb.put('/'+dataid,'start',0)
        try:
            if int(event.message.text) == fdb.get('/'+dataid,'answer'):
                message = TextSendMessage(text= username.display_name + " 答對了！共花了{}次".format(count))
                line_bot_api.reply_message(event.reply_token, message)
                fdb.put('/'+dataid,'start',0)
            elif not min < int(event.message.text) < max:
                message = TextSendMessage(text= "請從{}到{}中猜喔！".format(min,max) )
                line_bot_api.reply_message(event.reply_token, message)
                
            elif int(event.message.text) > fdb.get('/'+dataid,'answer'):
                fdb.put('/'+dataid,'max',int(event.message.text) )
                max = int(event.message.text) 
                message = TextSendMessage(text= "請從{}到{}中猜個數字".format(min,max) )
                line_bot_api.reply_message(event.reply_token, message)
            else:
                fdb.put('/'+dataid,'min',int(event.message.text) )
                min = int(event.message.text) 
                message = TextSendMessage(text= "請從{}到{}中猜個數字".format(min,max) )
                line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text= "還在猜數字中喔！請猜中或輸入「結束」來跳出" )
            line_bot_api.reply_message(event.reply_token, message)
    elif fdb.get('/'+dataid,'startaudio') == 1:
        if event.message.text == "結束":  
            message = TextSendMessage(text= "遊戲已終止，想再玩一次請輸入「開始猜音」" )
            line_bot_api.reply_message(event.reply_token, message)
            fdb.put('/'+dataid,'startaudio',0)
        elif event.message.text == fdb.get('/'+dataid,'audioanswer'):
            message = TextSendMessage(text= "答對了！好厲害！" )
            line_bot_api.reply_message(event.reply_token, message)
            fdb.put('/'+dataid,'startaudio',0)
        else:
            message = TextSendMessage(text= "不對喔！再猜一次～" )
            line_bot_api.reply_message(event.reply_token, message)
            
            
    else:
        UserName = event.source.user_id
        username = line_bot_api.get_profile(UserName)
        body = {
        'to':username.user_id,
        'messages':[{
                'type': 'text',
                'text': 'hello '+username.display_name
                
            }]
        }
        message = TextSendMessage(text= 'hello '+username.display_name )
        line_bot_api.reply_message(event.reply_token, message)

        # req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
       
        #message = TextSendMessage(text= username.display_name + username.user_id)
        #向指定網址發送request
        #req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
        # 印出得到的結果
        
        #line_bot_api.reply_message(event.reply_token, message)
        #fdb.put('/'+dataid,'test',event.message.text)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


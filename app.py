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
headers = {'Authorization':'Bearer '+os.environ['CHANNEL_ACCESS_TOKEN'],'Content-Type':'application/json'}

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
            order_message = event.message.text
            orders = order_message.split('\n')
            chn = ['','A','B','C','D','E','F','G']
            nn = len(fdb.get('/'+dataid+'/order','').values())
            try:
                nn = len(fdb.get('/'+dataid+'/order','').values())
            except:
                nn = 0
            messagetext = '已新增\n'
            for i in range(1,len(orders)):
                print(orders[i])
                
                fdb.put('/'+dataid+'/order/'+chn[nn+i],'店家',orders[i].split(',')[0])
                fdb.put('/'+dataid+'/order/'+chn[nn+i],'貨物',orders[i].split(',')[1])
                fdb.put('/'+dataid+'/order/'+chn[nn+i],'數量',orders[i].split(',')[2])

                messagetext = messagetext + '店家: '+orders[i].split(',')[0]+ ', 貨物: ' +orders[i].split(',')[1] + ', 數量: ' + orders[i].split(',')[2] + '\n'
            message = TextSendMessage(text= messagetext)
            line_bot_api.reply_message(event.reply_token, message)
        if event.message.text[:2] == '查詢':
            messagetext = ''
            for order in fdb.get('/Cbfe6adcef9ea0a171e91fcd7b5e6f184/order','').values():
                for ki,vi in zip(order.keys(),order.values()):
                    messagetext = messagetext + ki + ' ' + vi+', '
                messagetext = messagetext[:-2] + '\n'
            message = TextSendMessage(text= messagetext)
            line_bot_api.reply_message(event.reply_token, message)
        if event.message.text[:2] == '登記送貨':
            body = {
            'to':dataid,
            'messages':[{
                    'type': 'text',
                    'text': 'hello '+username.display_name
                    
                }]
            }
            print(body)
            req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
            

        
    
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


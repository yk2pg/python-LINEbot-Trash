#!/usr/bin/env python
# coding: utf-8

# In[27]:


#---------- Messaging API ----------#
import json
import calendar
import datetime
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage
import gspread

def main(event, context):
    with open('secret.json', 'r') as f:
        api = json.load(f) #secret.jsonからuser_IDとchannel_tokenを取得
        
    bot_api = LineBotApi(api['access_token']) #インスタンス化

    #翌日取得
    # import calendar
    # import datetime
    global nth_week
    global get_nth_dow

    def get_nth_week(day):
        nth_week = (day - 1) // 7 + 1
        return nth_week

    def get_nth_dow(year, month, day):
        get_nth_dow = get_nth_week(day), calendar.weekday(year, month, day)
        return get_nth_dow

    today = datetime.datetime.now() #現在日時取得
    tomorrow = today + datetime.timedelta(days=1) #現在日時に＋１日のタイムデルタを加算
    tom_nth_dow = get_nth_dow(tomorrow.year, tomorrow.month, tomorrow.day) #明日の(第n週、X曜日)を取得

    print("today:", today)
    print("tomorrow:", tomorrow)
    print("tom_nth_dow:", tom_nth_dow)

    #---------- ゴミの日 ----------#
    #import pandas as pd
    schedule=pd.DataFrame([
    ["Mon" ,"Tue"                 ,"Wed"        ,"Thurs" ,"Fri"                               ,"Sat"          , "Sun"],
    [""        ,"びん・缶・プラ" ,"可燃ごみ"   ,""         ,"不燃ごみ・古紙・ペット"  ,"可燃ごみ"   ,""    ],
    [""        ,"びん・缶・プラ" ,"可燃ごみ"   ,""         ,"古紙・ペット"  ,"可燃ごみ"   ,""    ],
    [""        ,"びん・缶・プラ" ,"可燃ごみ"   ,""         ,"不燃ごみ・古紙・ペット"  ,"可燃ごみ"   ,""    ],
    [""        ,"びん・缶・プラ" ,"可燃ごみ"   ,""         ,"古紙・ペット"  ,"可燃ごみ"   ,""    ],
    [""        ,"びん・缶・プラ" ,"可燃ごみ"   ,""         ,"古紙・ペット"  ,"可燃ごみ"   ,""   ],
    ])
    print(schedule)

    #---------- 住人一覧取得 ----------#
    #import gspread

    # サービスアカウントキーファイルの読み込み
    gspread_client = gspread.service_account(filename="./roof-dev-trash-a3e80ece4449.json")

    #スプレッドシート/roof_memberから読み込み
    member_sheet = gspread_client.open("roof_member")
    num = member_sheet.sheet1.col_values(1) #list 部屋番号(データ型)
    num = list(map(int, num)) #int型に変換、かつlistにする
    name = member_sheet.sheet1.col_values(2) #list 名前
    member = dict(zip(num,name)) #listからdictに変換

    #スプレッドシート/latest_memberから読み込み
    latest_member_sheet = gspread_client.open("latest_member")
    latest_num = latest_member_sheet.sheet1.col_values(1) #list 部屋番号(データ型)
    latest_num = latest_num[0] #int型
    latest_name = latest_member_sheet.sheet1.col_values(2) #list 名前
    latest_member = dict(zip(latest_num, latest_name)) #listからdictに変換

    #次の担当者
    latest_num = int(latest_num)
    next_num = latest_num + 1
    if next_num == 19:
        next_num = 1
    next_name = member.get(next_num)

    while next_num <= 18 and next_name == 'null':
        next_num += 1
        next_name = member.get(next_num)
    else:
        print(next_name)
        
    #---------- メッセージ作成 ----------#
    date_jp = ['月','火','水','木','金',"土",'日']

    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    tom_nth_dow = get_nth_dow(tomorrow.year, tomorrow.month, tomorrow.day)
    date_check = schedule.iat[tom_nth_dow]

    print("明日は第"+str(tom_nth_dow[0])+date_jp[tom_nth_dow[1]]+"曜日")
    print(date_check+"回収の日です")

    text1 = "第"+str(tom_nth_dow[0])+date_jp[tom_nth_dow[1]]+"曜日"
    text2 = "明日は"+text1+"で、\n"+date_check+"収集の日です！\n\n" 
    text3 = "担当は"+next_name+"だよ〜！\nよろしくね◎"

    #---------- メッセージ送信 ----------#
    if date_check =="":
        user_id = api['userid'] #IDを取得
        messages = TextSendMessage(text="明日のゴミ出しは有りません") #LINEに送付するメッセージ
        bot_api.push_message(user_id, messages=messages)
    else: 
        user_id = api['userid'] #IDを取得
        messages = TextSendMessage(text=text2 + text3) #LINEに送付するメッセージ
        bot_api.push_message(user_id, messages=messages)
        #次の担当者ファイル書き込み
        latest_member_sheet.sheet1.update_cell(1, 1, next_num)
        latest_member_sheet.sheet1.update_cell(1, 2, next_name)


# In[ ]:





# In[ ]:

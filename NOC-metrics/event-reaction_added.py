from cgitb import reset
import os
from urllib import response
from six.moves import urllib
import json
import datetime
import boto3

# todo
# время первого ответа
# asdfghjk
# данные 

def is_bot(event):
    return 'bot_profile' in event['event']

def has_reaction(event):
    return 'reaction_added' in event['event']['type']

def message_has_resume(event):
    return not is_bot(event) and has_reaction(event)

def send_text_response(event):
    SLACK_URL = "https://slack.com/api/chat.postMessage" # use postMessage if we want visible for everybody
    channel_id = event["event"]["item"]["channel"]
    user = event["event"]["user"]
    bot_token = os.environ["BOT_TOKEN"]
    ts = event["event"]["item"]["ts"]       #начало события или треда
    event_ts = event["event"]["event_ts"]   #время события
    def reaction():                         #извлечение реакции
        return event["event"]["reaction"]

  #расчет разницы времени между сообщением и реакцией
    def td(event_ts, ts):
        
     res = int(float(event_ts) - float(ts))
     
     days = res//86400
     hours = (res - days*86400)//3600
     minutes = (res - days*86400 - hours*3600)//60
     seconds = res - days*86400 - hours*3600 - minutes*60
     result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
                ("{0} hour{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
                ("{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
                ("{0} second{1}, ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
     return result
    
    # ===== db part
    client = boto3.resource('dynamodb')
    table = client.Table("metrics-db")
    table.put_item(Item= {'event-ts': event_ts,'ts': ts, 'user': user, 'text': reaction(), 'channel_id': channel_id, 'wested-time': td(event_ts, ts)})
    # ===== end db part

    data = urllib.parse.urlencode({
            "token": bot_token,
            "channel": channel_id,
            "thread_ts": ts,                #reply in thread
            "text":  "I see :"+reaction()+": datetime "+datetime.datetime.fromtimestamp(float(event_ts)).isoformat(sep=' ',timespec='seconds')+" Wasted "+td(event_ts, ts), 
            "user": user,
            "link_names": True
        })
    data = data.encode("ascii")
    request = urllib.request.Request(SLACK_URL, data=data, method="POST")
    request.add_header( "Content-Type", "application/x-www-form-urlencoded" )
    res = urllib.request.urlopen(request).read()


def lambda_handler(event, context):
    event = json.loads(event["body"])
    if message_has_resume(event):
        send_text_response(event)

    
    return {
        'statusCode': 200,
        'body': 'OK'
    }
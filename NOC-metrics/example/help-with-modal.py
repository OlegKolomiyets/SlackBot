import os
from six.moves import urllib
import json
import base64
import urllib.parse as parse
import boto3
from botocore.exceptions import ClientError

REPLYWORDS = [
    'help',
    'error'
]

BLOCK_REPLY_V2 = """
[
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "To quickly help you please select one of the button below and fill out the form with the information"
        }
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Report a Bug or Issue",
                    "emoji": true
                },
                "value": "help_me",
                "action_id": "help_me"
            }
        ]
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "New Module or Options",
                    "emoji": true
                },
                "value": "new_module",
                "action_id": "new_module"
            }
        ]
    },
    {
        "type": "divider"
    },
    {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": ":page_facing_up: <https://docs.ansible.com/ansible/devel/collections/index.html|Ansible Documentation> :page_facing_up: --  :Github: <https://github.com/ansible-collections?q=netapp&type=&language=&sort=| NetApp Github Repos> :Github:"
            }
        ]
    }
]
"""

BLOCK_MODAL = """
{
	"type": "modal",
	"callback_id": <callid>,
	"title": {
		"type": "plain_text",
		"text": "Ansible Helper",
		"emoji": true
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": true
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": true
	},
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Ansible_bug_report",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "ansible_version"
			},
			"label": {
				"type": "plain_text",
				"text": "Ansible Version",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible --version"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "system_version"
			},
			"label": {
				"type": "plain_text",
				"text": "ONTAP / Cloud Manager version",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible --version"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "collection_version"
			},
			"label": {
				"type": "plain_text",
				"text": "Ansible collection version",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible-galaxy collection list"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "problem"
			},
			"label": {
				"type": "plain_text",
				"text": "Description of the problem",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "playbook"
			},
			"label": {
				"type": "plain_text",
				"text": "Playbook",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "error"
			},
			"label": {
				"type": "plain_text",
				"text": "Debug output of your playbook",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible-playbook <your playbook> -vvv"
			}
		}
	]
}
"""

NEW_MODULE_MODAL = """
{
	"type": "modal",
	"callback_id": <callid>,
	"title": {
		"type": "plain_text",
		"text": "Ansible Helper",
		"emoji": true
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": true
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": true
	},
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Ansible_new_feature",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "collection"
			},
			"label": {
				"type": "plain_text",
				"text": "Which Collection",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "new_module"
			},
			"label": {
				"type": "plain_text",
				"text": "Description of what you are trying to do or what option is missing",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "example"
			},
			"label": {
				"type": "plain_text",
				"text": "Example of how you are doing this today",
				"emoji": true
			}
		}
	]
}
"""


def send_text_response(blocks, channel_id=None, thread_ts=None, user=None):
    # use postMessage if we want visible for everybody
    # use postEphemeral if we want just the user to see
    slack_url = "https://slack.com/api/chat.postMessage"
    channel_id = channel_id
    user = user
    bot_token = os.environ["BOT_TOKEN"]
    thread_ts = thread_ts
    data = urllib.parse.urlencode({
        "token": bot_token,
        "channel": channel_id,
        "blocks": blocks,
        "user": user,
        "link_names": True,
        "parse": True,
        "thread_ts": thread_ts
    })
    data = data.encode("utf-8")
    print(data)
    request = urllib.request.Request(slack_url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    res = urllib.request.urlopen(request).read()
    print('res:', res)


def send_modal(trigger_id, modal):
    slack_url = 'https://slack.com/api/views.open'
    bot_token = os.environ["BOT_TOKEN"]
    data = urllib.parse.urlencode({
        "token": bot_token,
        "trigger_id": trigger_id,
        "view": modal
    })
    data = data.encode("utf-8")
    print(data)
    request = urllib.request.Request(slack_url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    res = urllib.request.urlopen(request).read()
    print('res:', res)


def parse_message(event):
    if not is_bot(event) and event["text"] in REPLYWORDS:
        send_text_response(BLOCK_REPLY_V2, event['channel'], event['ts'], event['user'])
        add_thread_to_database(event)
    else:
        print(is_bot(event))


# def add_thread_to_database(event):
#     dynamodb = boto3.client('dynamodb')
#     key_dic = {'ts': {'S': event['ts']},
#                'user': {'S': event['user']},
#                'channel': {'S': event['channel']},
#                'text': {'S': event['text']}}
#     dynamodb.put_item(TableName='ts-recorder', Item=key_dic)


# def get_thread_from_database(thread_id):
#     table = boto3.resource('dynamodb').Table('ts-recorder')
#     try:
#         response = table.get_item(Key={'ts': thread_id})
#     except ClientError as e:
#         print(e.response['Error']['Message'])
#     else:
#         return response['Item']


# def update_thread_to_datebase(thread_ts, message):
#     table = boto3.resource('dynamodb').Table('ts-recorder')
#     response = table.update_item(
#         Key={'ts': thread_ts},
#         AttributeUpdates=message,
#         ReturnValues="ALL_NEW"
#     )
#     print('Update Response: ' + response)


def parse_button_push(event):
    trigger_id = event['trigger_id']
    thread_ts = event['container']['thread_ts']
    if event['actions'][0]['action_id'] == 'help_me':
        modal = BLOCK_MODAL
    if event['actions'][0]['action_id'] == 'new_module':
        modal = NEW_MODULE_MODAL
    modal = update_modal(modal, thread_ts)
    send_modal(trigger_id, modal)


def update_modal(modal, thread_ts):
    callid = '"' + str(thread_ts) + '"'
    return modal.replace('<callid>', callid)


def parse_modal_submit(event):
    message, thread_ts, channel_id, user = parse_responce(event)
    update_thread_to_datebase(thread_ts, message)


def parse_responce(event):
    message = {}
    if event['view']['blocks'][0]['text']['text'] == "Ansible_bug_report":
        for block in event['view']['state']['values']:
            for key in event['view']['state']['values'][block]:
                message[key] = {"Action": "PUT", "Value": event['view']['state']['values'][block][key]['value']}
    if event['view']['blocks'][0]['text']['text'] == "Ansible_new_feature":
        for block in event['view']['state']['values']:
            for key in event['view']['state']['values'][block]:
                message[key] = {"Action": "PUT", "Value": event['view']['state']['values'][block][key]['value']}
    thread_ts = (event['view']['callback_id'])
    db_record = get_thread_from_database(thread_ts)
    user = event['user']['username']
    return message, thread_ts, db_record['channel'], user


def create_responce_message(message, return_text):
    return_message = return_text
    for each in message:
        return_message = insert_string(return_message, (each + ':'), (' ' + message[each]))
    # return_message = parse.quote(return_message)
    return return_message


def insert_string(message, cut_point, string_to_add):
    index = message.rfind(cut_point)
    cut_point_len = len(cut_point)
    return message[:(index + cut_point_len)] + string_to_add + message[(index + cut_point_len):]


def is_bot(event):
    return 'bot_profile' in event


def covert_base_64(event):
    """
    Covert a base 64 message that json can understand
    :param event: Event from slack in base64
    :return: Event in string format
    """
    body = event.get("body", "")
    body = base64.b64decode(body).decode("utf-8")
    # Decoding the base64 return leave all the %22 URL charters, this coverts them to there utf-8 form
    body = parse.unquote(body)
    # Something above cause this to not be valid json, to fix this we just strip the payload= part out, and we get valid json
    body = body.split('payload=')[1]
    event = json.loads(body)
    return event


def lambda_handler(event, context):
    if event["isBase64Encoded"]:
        event = covert_base_64(event)
    else:
        event = json.loads(event["body"])
        event = event['event']
    print('event', event)
    if event['type'] == 'message':
        print('message')
        parse_message(event)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    if event['type'] == 'block_actions':
        print('block_actions')
        parse_button_push(event)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    if event['type'] == 'view_submission':
        print('view_submission')
        parse_modal_submit(event)
        return {
            "response_action": "clear"
        }

    return {
        'statusCode': 200,
        'body': 'OK'
    }
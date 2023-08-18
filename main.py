'''
The idea for this cloud function is to handle the incoming request in few steps:
- Check if the event type is "join" for group join and disregard other types
    - Check if the GroupID not in the FireBase DB
        - Create the new entry with GroupID and URL
        - Reply the "join" message to Line API with newly created URL
    - Otherwise reply "already exists" message
'''
import os
import random

import functions_framework
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import JoinEvent

database = None # instance of a database

# Line API requires a token for authorization
# Handler needs secret to check against the signature
line_api = Configuration(access_token=str(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')))
handler = WebhookHandler(str(os.environ.get('LINE_CHANNEL_SECRET')))


def generate_custom_url(length=10):
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    custom_url = ''.join(random.choice(characters) for _ in range(length))
    return custom_url


@functions_framework.http
def webhook(request):
    '''HTTP Cloud Function. 
    
    Args:
        request (flask.Request): The request object.

    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`.
    '''
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Abort', 400
    
    return 'OK'


@handler.add(JoinEvent)
def handle_join_event(event: JoinEvent):
    group_id = event.source.groupId
    
    line_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=f'Group ID: {group_id}')]
        )
    )
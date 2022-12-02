# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)


def send_welcome_message(to, from_, group_name):
    message = client.messages \
                .create(
                     body=f"Welcome to {group_name}! You can post to the group by responding to this number.",
                     from_=from_,
                     to=to
                 )
    print(message.sid)


def send_message(to, from_, body):
    message = client.messages \
                .create(
                     body=body,
                     from_=from_,
                     to=to
                 )
    print(message.sid)
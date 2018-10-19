#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from flask import abort, Flask, jsonify, request, Response
from attrdict import AttrDict

from slackclient import SlackClient

from utils.fmt import *

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
SLACK_TEAM_ID = os.environ['SLACK_TEAM_ID']

slack = SlackClient(SLACK_BOT_TOKEN)

### incoming webhooks
### https://hooks.slack.com/services/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

def is_request_valid(token, team_id):
    return token == SLACK_VERIFICATION_TOKEN and team_id == SLACK_TEAM_ID

@app.route('/props-bot', methods=['POST'])
def props_bot():
    form = AttrDict(request.form.to_dict())
    dbg(form)
    if not is_request_valid(form.token, form.team_id):
        abort(400)

    return 'wazzup playa?', 200

@app.route('/slack/interactivity', methods=['POST'])
def slack_interactivity():
    json = AttrDict(request.get_json(silent=True))
    dbg(json)
    return Response(), 200

@app.route('/slack/message-menus', methods=['POST'])
def slack_message_menus():
    json = AttrDict(request.get_json(silent=True))
    dbg(json)
    return Response(), 200

@app.route('/slack/events', methods=['POST'])
def slack_events():
    json = AttrDict(request.get_json(silent=True))
    if 'challenge' in json:
        return json.challenge, 200
    dbg(json)
    channels = slack.api_call('channels.list')['channels']
    dbg(channels)
    channel_info = slack.api_call('channels.info', channel=SLACK_TEAM_ID)
    dbg(channel_info)
    users = slack.api_call('users.list')['members']
    dbg(users)
    return Response(), 200



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
props bot
'''

import os

from json import dumps
from ruamel import yaml
from quart import abort, Quart, request, Response
from quart.helpers import make_response
from attrdict import AttrDict
from slackclient import SlackClient

from utils.dbg import dbg
from utils.dictionary import merge
from config import CFG

from propsbot import PropsBot

app = Quart(__name__)


SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_NAME = os.path.basename(SCRIPT_FILE)
SCRIPT_PATH = os.path.dirname(SCRIPT_FILE)
CONTRIBUTE_JSON = yaml.safe_load(open(f'{SCRIPT_PATH}/contribute.json'))

PROPS = {}

async def jsonify(status=200, indent=4, sort_keys=True, **kwargs):
    '''
    async jsonify
    '''
    response = await make_response(dumps(dict(**kwargs), indent=indent, sort_keys=sort_keys)+'\n')
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = status
    return response

### incoming webhooks
### https://hooks.slack.com/services/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


def is_request_valid(token, team_id):
    '''
    is_request_valid
    '''
    return token == CFG.SLACK_VERIFICATION_TOKEN and team_id == CFG.SLACK_TEAM_ID

@app.route('/version', methods=['GET'])
async def version():
    '''
    async version route
    '''
    return f'{CFG.APP_VERSION}\n', 200

@app.route('/contribute.json', methods=['GET'])
async def contribute_json():
    '''
    async contribute.json route
    '''
    json = merge(CONTRIBUTE_JSON, dict(
        repository=dict(
            version=CFG.APP_VERSION,
            revision=CFG.APP_REVISION)))
    response = await jsonify(**json), 200
    return response

@app.route('/props-bot', methods=['POST'])
async def props_bot():
    '''
    async props_bot slash command route
    '''
    form = await request.form.to_dict()
    form = AttrDict(form)
    if not is_request_valid(form.token, form.team_id):
        abort(400)

    return 'wazzup playa?', 200

@app.route('/slack/interactivity', methods=['POST'])
async def slack_interactivity():
    '''
    async slack_interactivity route
    '''
    json = await request.get_json(silent=True)
    json = AttrDict(json)
    return Response('', status=200)

@app.route('/slack/message-menus', methods=['POST'])
async def slack_message_menus():
    '''
    async slack_message_menus route
    '''
    json = await request.get_json(silent=True)
    json = AttrDict(json)
    return Response('', status=200)

@app.route('/slack/events', methods=['POST'])
async def slack_events():
    '''
    async slack_events route
    '''
    print('*'*80)
    json = await request.get_json(silent=True)
    json = AttrDict(json)
    if 'challenge' in json:
        return json.challenge, 200
    if json.event.channel != CFG.PROPS_BOT_CHANNEL_ID and 'text' in json.event:
        return Response('', status=200)
    if json.event.get('username', None) == 'props':
        return Response('', status=200)

    dbg(event=json.event)
    slack = SlackClient(CFG.BOT_USER_OAUTH_ACCESS_TOKEN)
    bot = PropsBot(slack, json.event)
    name, prop, operator, operand = bot.parse()
    dbg(name, prop, operator, operand)
    if name in bot.members_in_channel:
        bot.update(name, prop, operator, operand)
    return Response('', status=200)

async def io_background_task():
    '''
    async io_background_task
    '''
    raise NotImplementedError

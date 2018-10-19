#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
propsbot
'''

import re

from attrdict import AttrDict

from utils.dbg import dbg

#pylint: disable=line-too-long
parse_regex = re.compile(r'(?P<name>[A-Za-z0-9_-]+)(:(?P<prop>[A-Za-z0-9_-]+))?(?P<operator>\+\+|--|\+=|-=)?(?P<operand>[0-9])?')

class EventTextError(Exception):
    '''
    EventTextError
    '''
    def __init__(self, json):
        '''
        init
        '''
        msg = f'event.text error; json = {json}'
        super(EventTextError, self).__init__(msg)

class EventChannelError(Exception):
    '''
    EventChannelError
    '''
    def __init__(self, json):
        '''
        init
        '''
        msg = f'event.channel error; json = {json}'
        super(EventChannelError, self).__init__(msg)

class ChannelsListError(Exception):
    '''
    ChannelsListError
    '''
    def __init__(self, json):
        '''
        init
        '''
        msg = f'channels.list error; json = {json}'
        super(ChannelsListError, self).__init__(msg)

class ChannelsInfoError(Exception):
    '''
    ChannelsInfoError
    '''
    def __init__(self, json):
        '''
        init
        '''
        msg = f'channels.info error; json = {json}'
        super(ChannelsInfoError, self).__init__(msg)

class MembersListError(Exception):
    '''
    MembersListError
    '''
    def __init__(self, json):
        '''
        init
        '''
        msg = f'users.list error; json = {json}'
        super(MembersListError, self).__init__(msg)

class PropsBot:
    '''
    PropsBot
    '''
    props = {}

    operators = {
        '++': lambda x, y: x + 1,
        '--': lambda x, y: x - 1,
        '+=': lambda x, y: x + int(y),
        '-=': lambda x, y: x - int(y),
    }

    def __init__(self, slack, event):
        '''
        init
        '''
        self.slack = slack
        self.event = event

    @property
    def has_connectivity(self):
        '''
        has_connectivity
        '''
        api_test = self.slack.api_call('api.test')
        auth_test = self.slack.api_call('auth.test')
        dbg(api_test, auth_test)
        return True

    @property
    def text(self):
        '''
        text
        '''
        if 'text' in self.event:
            return self.event.text
        raise EventTextError(self.event)

    @property
    def channel(self):
        '''
        channel
        '''
        if 'channel' in self.event:
            return self.event.channel
        raise EventChannelError(self.event)

    @property
    def channels(self):
        '''
        channels
        '''
        json = self.slack.api_call('channels.list')
        if 'channels' in json:
            return [AttrDict(channel) for channel in json['channels']]
        raise ChannelsListError(json)

    @property
    def channels_info(self):
        '''
        channels_info
        '''
        json = self.slack.api_call('channels.info', channel=self.channel)
        if 'channel' in json:
            return AttrDict(json['channel'])
        raise ChannelsInfoError(json)

    @property
    def members(self):
        '''
        members
        '''
        json = self.slack.api_call('users.list')
        if 'members' in json:
            return [AttrDict(member) for member in json['members']]
        raise MembersListError(json)

    @property
    def members_in_channel(self):
        '''
        members_in_channel
        '''
        return [member.name for member in self.members if member.id in self.channels_info.members]

    def parse(self, text=None):
        '''
        parse
        '''
        match = parse_regex.search(text if text else self.text)
        if match:
            d = match.groupdict()
            return d['name'], d['prop'], d['operator'], d['operand']
        return [None] * 4

    def send(self, message, channel=None):
        '''
        send
        '''
        self.slack.api_call('chat.postMessage', channel=channel if channel else self.channel, text=message)

    def update(self, name, prop, operator, operand):
        '''
        update
        '''
        dbg()
        if operator:
            member_props = PropsBot.props.pop(name, {})
            prop_value = member_props.pop(prop, 0)
            member_props[prop] = PropsBot.operators[operator](prop_value, operand)
            PropsBot.props[name] = member_props
        value = PropsBot.props.get(name, {}).get(prop, 0)
        message = f'{name}:{prop} => {value}'
        self.send(message)

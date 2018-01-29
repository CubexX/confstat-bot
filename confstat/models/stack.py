# -*- coding: utf-8 -*-
__author__ = 'CubexX'

import time

from .chatstat import ChatStat
from confstat import cache


class Stack:
    stack = []

    def add(self, obj):
        self.stack.append(obj)

    def send(self):
        cids_list = self.stack
        all_messages = 0

        # WTF???
        # TODO: fix this
        counter = {x['cid']: {'msgs': 0, 'usrs': 0} for x in cids_list}
        for cid in counter.keys():
            counter[cid]['msg'] = sum([a['msg_count'] for a in cids_list if a['cid'] == cid])
            counter[cid]['usr'] = sum([a['users_count'] for a in cids_list if a['cid'] == cid])

        for x in counter.items():
            cid = x[0]
            msg_count = x[1]['msg']
            users_count = x[1]['usr']
            all_messages += msg_count

            ChatStat().add(cid,
                           users_count,
                           msg_count,
                           int(time.time()))

        # Statistics for admin panel
        c = cache.get('today_messages')

        if c:
            cache.incr('today_messages', all_messages)
        else:
            cache.set('today_messages', all_messages, 86400)

        cids_list.clear()

    def clear(self):
        self.stack.clear()

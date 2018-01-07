# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from .chatstat import ChatStat
import time


class Stack:
    stack = []

    def add(self, obj):
        self.stack.append(obj)

    def send(self):
        cids_list = self.stack

        # WTF???
        # TODO: fix this
        counter = {x['cid']: {'msgs': 0, 'usrs': 0} for x in cids_list}
        for ccid in counter.keys():
            counter[ccid]['msg'] = sum([a['msg_count'] for a in cids_list if a['cid'] == ccid])
            counter[ccid]['usr'] = sum([a['users_count'] for a in cids_list if a['cid'] == ccid])

        for x in counter.items():
            cid = x[0]
            msg_count = x[1]['msg']
            users_count = x[1]['usr']

            ChatStat().add(cid,
                           users_count,
                           msg_count,
                           int(time.time()))

        cids_list.clear()

    def clear(self):
        self.stack.clear()

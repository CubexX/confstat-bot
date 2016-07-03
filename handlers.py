# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from models import Entity, Chat, User, UserStat, Stack, Stats, ChatStat
from datetime import datetime, timedelta
from telegram import ParseMode
from config import CONFIG
from main import cache
import logging
import time
import re

logger = logging.getLogger(__name__)


def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    bot.sendMessage(chat_id, '/stat\n/me')


def stat(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type

    last_call = cache.get('last_{}'.format(chat_id))

    if not last_call:
        cache.set('last_{}'.format(chat_id), int(time.time()) + 5)
        last_call = int(time.time()) + 5

    if (int(time.time()) - last_call) >= 5:
        if chat_type == 'group' or chat_type == 'supergroup':
            msg = '{}/group/{}\n'.format(CONFIG['site_url'], chat_id)
            info = Stats().get_chat(chat_id)

            msg += 'Сообщений: {}\n' \
                   'Активных пользовтелей: {}\n\n' \
                   'Топ-5:\n{}\n'.format(info['msg_count'],
                                         info['current_users'],
                                         info['top_users'])
            if info['popular_links'] is not '':
                msg += 'Популярные ссылки:\n{}'.format(info['popular_links'])

            bot.sendMessage(chat_id, msg, parse_mode=ParseMode.MARKDOWN)
            # Update last call
            cache.set('last_{}'.format(chat_id), int(time.time()))


def me(bot, update):
    msg_id = update.message.message_id
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user_fullname = " ".join([update.message.from_user.first_name,
                              update.message.from_user.last_name])
    chat_type = update.message.chat.type

    if chat_type == 'private':
        info = Stats().get_user(user_id)
        groups = ''

        i = 0
        for group in info['groups']:
            i += 1

            info = Stats().get_user(user_id, group)

            groups += ' *{}. {}* — {} ({}%)\n'.format(i,
                                                      Chat().get(group).title,
                                                      info['group_msg_count'],
                                                      info['percent'])

        msg = 'Всего сообщений: {}\n' \
              'Список групп:\n' \
              '{}'.format(info['msg_count'],
                          groups)

        bot.sendMessage(chat_id, msg, parse_mode=ParseMode.MARKDOWN)

    if chat_type == 'group' or chat_type == 'supergroup':
        info = Stats().get_user(user_id, chat_id)
        msg = Stats().me_format(user_fullname,
                                username,
                                info['group_msg_count'],
                                info['percent'],
                                info['msg_count'])

        bot.sendMessage(chat_id, msg, reply_to_message_id=msg_id)


def message(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    msg = update.message.text

    username = update.message.from_user.username
    user_fullname = " ".join([update.message.from_user.first_name,
                              update.message.from_user.last_name])

    chat_type = update.message.chat.type
    chat_title = update.message.chat.title

    # If message from group
    if chat_type == 'group' or chat_type == 'supergroup':
        # Add chat and user to DB
        User().add(user_id, username, user_fullname)
        Chat().add(chat_id, chat_title)

        if update.message.photo:
            Entity().add(chat_id, 'photo', None)

        if update.message.video:
            Entity().add(chat_id, 'video', None)

        if update.message.audio:
            Entity().add(chat_id, 'audio', None)

        if update.message.voice:
            Entity().add(chat_id, 'voice', None)

        if update.message.document:
            Entity().add(chat_id, 'document', None)

        for entity in update.message.entities:

            # http://link.com
            if entity['type'] == 'url':
                link = msg[entity['offset']:entity['offset'] + entity['length']]
                link = re.sub('(.*)://', '', link)
                link = link.split('/')[0]
                Entity().add(cid=chat_id, type='url', title=link)

            # /command
            if entity['type'] == 'bot_command':
                title = msg[entity['offset']:entity['offset'] + entity['length']]
                Entity().add(cid=chat_id, type='bot_command', title=title)

            # #hashtag
            if entity['type'] == 'hashtag':
                title = msg[entity['offset']:entity['offset'] + entity['length']]
                Entity().add(cid=chat_id, type='hashtag', title=title)

            # @username
            if entity['type'] == 'mention':
                title = msg[entity['offset']:entity['offset'] + entity['length']]
                Entity().add(cid=chat_id, type='mention', title=title)

        user_stat = UserStat().get(user_id, chat_id)

        # If user already in group
        if user_stat:
            today = datetime.today().day
            last_activity = datetime.fromtimestamp(timestamp=user_stat.last_activity).day

            # If last activity was not today
            if (timedelta(today).days - timedelta(last_activity).days) != 0:
                Stack().add({'cid': chat_id,
                             'msg_count': 1,
                             'users_count': 1})
            else:
                Stack().add({'cid': chat_id,
                             'msg_count': 1,
                             'users_count': 0})
        else:
            Stack().add({'cid': chat_id,
                         'msg_count': 1,
                         'users_count': 1})
        # Update user messages count
        UserStat().add(user_id, chat_id)
    else:  # If message from user
        pass


def job(bot):
    Stack().send()


def update_to_supergroup(bot, update):
    old_id = update.message.migrate_from_chat_id
    new_id = update.message.chat_id
    user_id = update.message.from_user.id

    if old_id:
        UserStat().update(user_id, old_id, {'cid': new_id})
        Entity().update_all(old_id, {'cid': new_id})
        Chat().update(old_id, {'cid': new_id})
        ChatStat().update(old_id, {'cid': new_id})

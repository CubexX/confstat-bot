# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from models import Entity, Chat, User, UserStat, Stack, Stats, ChatStat, db
from datetime import datetime, timedelta
from telegram import ParseMode
from main import cache, CONFIG
import logging
import time
import re

logger = logging.getLogger(__name__)


def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    bot.sendMessage(chat_id, '/stat — get stats in group\n'
                             '/me — get your stats\n'
                             '/setprivacy — show/hide your stats\n\n'
                             'Like bot? [Rate it!](https://storebot.me/bot/confstatbot)\n\n'
                             'GitHub: [confstat-bot](https://github.com/CubexX/confstat-bot), '
                             '[confstat-web](https://github.com/CubexX/confstat-web)', parse_mode=ParseMode.MARKDOWN)


def stat(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    chat_title = update.message.chat.title

    last_call = cache.get('last_{}'.format(chat_id))

    # First request
    if not last_call:
        cache.set('last_{}'.format(chat_id), int(time.time()) - 5)
        last_call = int(time.time()) - 5

    # If last request was over 5 seconds ago
    if (int(time.time()) - last_call) >= 5:
        if chat_type == 'group' or chat_type == 'supergroup':
            # Get stats for group
            info = Stats.get_chat(chat_id)

            # Get msg text for /stat
            msg = Stats.stat_format(chat_id,
                                    info['msg_count'],
                                    info['current_users'],
                                    info['top_users'],
                                    chat_title)
            bot.sendMessage(chat_id, msg, parse_mode=ParseMode.MARKDOWN)

            # Update last call
            cache.set('last_{}'.format(chat_id), int(time.time()))
            logger.info('Group {} requested stats'.format(chat_id))


def me(bot, update):
    msg_id = update.message.message_id
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    fullname = " ".join([update.message.from_user.first_name,
                         update.message.from_user.last_name])
    chat_type = update.message.chat.type

    if chat_type == 'private':
        info = Stats.get_user(user_id)
        token = User.generate_token(user_id)
        msg = Stats.me_private_format(user_id, info['groups'], info['msg_count'], token)

        cache.set('user_token_{}'.format(user_id), token, 600)

        bot.sendMessage(chat_id, msg, parse_mode=ParseMode.MARKDOWN)

    if chat_type == 'group' or chat_type == 'supergroup':
        info = Stats.get_user(user_id, chat_id)
        msg = Stats.me_format(user_id,
                              fullname,
                              username,
                              info['group_msg_count'],
                              info['percent'],
                              info['msg_count'])

        bot.sendMessage(chat_id, msg, reply_to_message_id=msg_id, parse_mode=ParseMode.MARKDOWN)

    logger.info('User {} requested stats'.format(user_id))


def message(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    msg = update.message.text

    username = update.message.from_user.username
    fullname = " ".join([update.message.from_user.first_name,
                         update.message.from_user.last_name])

    chat_type = update.message.chat.type
    chat_title = update.message.chat.title

    # If message from group
    if chat_type == 'group' or chat_type == 'supergroup':
        # Add chat and user to DB
        User().add(user_id, username, fullname)
        Chat().add(chat_id, chat_title, bot.getChat(chat_id).username)

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

        user_stat = UserStat.get(user_id, chat_id)

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
        UserStat.update(user_id, old_id, {'cid': new_id})
        Entity.update_all(old_id, {'cid': new_id})
        Chat.update(old_id, {'cid': new_id})

        # Update all rows in chat_stats
        for c in db.query(ChatStat)\
                .filter(ChatStat.cid == old_id)\
                .all():
            c.cid = new_id
        db.commit()

        bot.sendMessage(new_id, 'Group was updated to supergroup')
        cache.delete('last_{}'.format(old_id))
        logger.info('Group {} was updated to supergroup {}'.format(old_id, new_id))


def set_privacy(bot, update):
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    msg_id = update.message.message_id

    user = User.get(user_id)

    if user:
        privacy = user.public

        if privacy:
            public = False
            msg = 'Your statistics is *private*'
        else:
            public = True
            msg = 'Your statistics is *public*'

        User.update(user_id, {'public': public})
        cache.delete('user_{}'.format(user_id))
    else:
        msg = 'User not found'

    bot.sendMessage(chat_id, msg, parse_mode=ParseMode.MARKDOWN, reply_to_message_id=msg_id)

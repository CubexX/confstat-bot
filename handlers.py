# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from models import db, Entity, Chat, User, UserStat, ChatStat, Stack
from config import SITE_URL, cache, logger
from telegram import ParseMode
import locale
import re

def number_format(num, places=0):
    return locale.format("%.*f", (places, num), True)

def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    bot.sendMessage(chat_id, 'Start message')


def stat(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type

    if chat_type == 'group':
        msg = '{}/group/{}\n'.format(SITE_URL, chat_id)
        all_msg_count = 0
        current_users = 0
        top_users = ''
        popular_links = ''

        q = db.query(ChatStat) \
            .filter(ChatStat.cid == chat_id) \
            .order_by(ChatStat.id.desc()) \
            .all()
        if q:
            for row in q:
                all_msg_count += row.msg_count
            current_users = q[0].users_count

        q = db.query(UserStat, User) \
            .join(User, User.uid == UserStat.uid) \
            .filter(UserStat.cid == chat_id) \
            .order_by(UserStat.msg_count.desc()) \
            .limit(5) \
            .all()
        if q:
            i = 0
            for stats, user in q: #generate top users
                i += 1
                if all_msg_count is not 0:
                    top_users += '  *{}. {}* — {} ({} %)\n'.format(i, user.fullname,
                                                    stats.msg_count, number_format(stats.msg_count * 100 / all_msg_count, 2))
                else:
                    top_users += '  *{}. {}* — {}\n'.format(i, user.fullname,
                                                    stats.msg_count)

        q = db.query(Entity) \
            .filter(Entity.cid == chat_id,
                    Entity.type == 'url') \
            .order_by(Entity.count.desc()) \
            .limit(3) \
            .all()
        if q:
            i = 0
            for url in q: #generate top links
                i += 1
                popular_links += '  *{}. {}* — {}\n'.format(i, url.title,
                                                        url.count)

        msg += ' Сообщений: {}\n' \
               ' Активных пользовтелей: {}\n\n' \
               ' Топ-5:\n{}\n\n' \
               ' Популярные ссылки:\n{}'.format(all_msg_count,
                                                current_users,
                                                top_users,
                                                popular_links)

        bot.sendMessage(chat_id, msg, parse_mode=ParseMode.MARKDOWN)


def me(bot, update):
    msg_id = update.message.message_id
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user_fullname = "{} {}".format(update.message.from_user.first_name,
                                   update.message.from_user.last_name)
    chat_type = update.message.chat.type

    if chat_type == 'group':
        user = UserStat().get(user_id, chat_id)
        all_msg_count = 0

        q = db.query(UserStat).filter(UserStat.uid == user_id).all()
        if q:
            for row in q:
                all_msg_count += row.msg_count

        if user:
            msg = '{} (@{}):\n' \
                  ' Сообщений в этом чате: {}\n' \
                  ' Сообщений всего: {}'.format(user_fullname,
                                                username,
                                                user.msg_count,
                                                all_msg_count)

            bot.sendMessage(chat_id, msg, reply_to_message_id=msg_id)


def message(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    msg = update.message.text

    username = update.message.from_user.username
    user_fullname = "{} {}".format(update.message.from_user.first_name,
                                   update.message.from_user.last_name)

    chat_type = update.message.chat.type
    chat_title = update.message.chat.title

    # If message from group
    if chat_type == 'group':
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

                if title == '/stat' or title == '/stat@confstatbot':
                    stat(bot, update)

                Entity().add(cid=chat_id, type='bot_command', title=title)

            # #hashtag
            if entity['type'] == 'hashtag':
                title = msg[entity['offset']:entity['offset'] + entity['length']]
                Entity().add(cid=chat_id, type='hashtag', title=title)

            # @username
            if entity['type'] == 'mention':
                title = msg[entity['offset']:entity['offset'] + entity['length']]
                Entity().add(cid=chat_id, type='mention', title=title)

        # If user already in group
        if UserStat().get(user_id, chat_id):
            Stack().add({'cid': chat_id,
                         'msg_count': 1,
                         'users_count': 0})
        else:
            Stack().add({'cid': chat_id,
                         'msg_count': 1,
                         'users_count': 1})
        # Update user messages count
        UserStat().add(user_id, chat_id, 1)
    else:  # If message from user
        pass


def job(bot):
    Stack().send()

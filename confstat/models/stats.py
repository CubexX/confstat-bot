# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from main import make_db_session
from .userstat import UserStat
from .chatstat import ChatStat
from config import CONFIG
from .chat import Chat
from .user import User
import locale


class Stats:
    @staticmethod
    @make_db_session
    def get_user(user_id, db, chat_id=None):
        all_msg_count = 0
        groups = []

        # All messages
        q = db.query(UserStat).filter(UserStat.uid == user_id).all()
        if q:
            for row in q:
                all_msg_count += row.msg_count
                groups.append(row.cid)

        if chat_id:
            user = UserStat.get(user_id, chat_id)
            if user:
                return {
                    'msg_count': all_msg_count,
                    'group_msg_count': user.msg_count,
                    'percent': Stats.number_format(user.msg_count * 100 / all_msg_count, 2)
                }

        return {
            'msg_count': all_msg_count,
            'groups': groups
        }

    @staticmethod
    @make_db_session
    def get_chat(chat_id, db):
        all_msg_count = 0
        current_users = 0
        top_users = ''

        # All messages in group and active users
        q = ChatStat().get(chat_id)
        if q:
            all_msg_count = q.msg_count
            current_users = q.users_count

        # Top-5 generation
        q = db.query(UserStat, User) \
            .join(User, User.uid == UserStat.uid) \
            .filter(UserStat.cid == chat_id) \
            .order_by(UserStat.msg_count.desc()) \
            .limit(5) \
            .all()
        if q:
            i = 0
            for stats, user in q:
                i += 1
                if all_msg_count is not 0:
                    percent = Stats.number_format(stats.msg_count * 100 / all_msg_count, 2)

                    top_users += ' *{0}. {1}* — {2} ({3}%)\n'.format(i, user.fullname,
                                                                     stats.msg_count,
                                                                     percent)
                else:
                    top_users += ' *{0}. {1}* — {2}\n'.format(i, user.fullname, stats.msg_count)

        return {
            'msg_count': all_msg_count,
            'current_users': current_users,
            'top_users': top_users
        }

    @staticmethod
    def number_format(num, places=0):
        return locale.format("%.*f", (places, num), True)

    @staticmethod
    def me_format(uid, fullname, username, group_msg_count, percent, msg_count):
        uname = ''
        if username is not '':
            uname = ' (@{})'.format(username)

        msg = '*{0}*{1}:\n' \
              ' Messages in this group: {2} ({3}%)\n' \
              ' Total messages: {4}\n\n' \
              '[More]({5}/user/{6})'.format(fullname,
                                            uname,
                                            group_msg_count,
                                            percent,
                                            msg_count,
                                            CONFIG['site_url'],
                                            uid)
        return msg

    @staticmethod
    def me_private_format(uid, group_list, msg_count, token):
        groups = ''

        # Group list generating
        i = 1
        for group in group_list:
            user_stats = Stats.get_user(uid, group)
            groups += ' *{0}. {1}* — {2} ({3}%)\n'.format(i,
                                                          Chat.get(group).title,
                                                          user_stats['group_msg_count'],
                                                          user_stats['percent'])
            i += 1

        msg = 'Total messages: {0}\n\n' \
              'Groups list:\n' \
              '{1}\n' \
              '[More]({2}/user/{3}/{4})'.format(msg_count,
                                                groups,
                                                CONFIG['site_url'],
                                                uid,
                                                token)
        return msg

    @staticmethod
    def stat_format(cid, msg_count, current_users, top_users, chat_title):
        msg = '*{2}*\n' \
              'Messages: {0}\n' \
              'Today active users: {1}\n\n'.format(msg_count, current_users, chat_title)
        if top_users is not '':
            msg += 'Top-5:\n{0}\n'.format(top_users)

        # Link to web-site with stats
        msg += '[More]({0}/group/{1})'.format(CONFIG['site_url'], ChatStat.generate_hash(cid))

        return msg

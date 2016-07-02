# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from sqlalchemy import Column, Integer, String, Text, BigInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from config import CONFIG
from main import cache
import locale
import time

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    uid = Column('uid', Integer)
    username = Column('username', Text)
    fullname = Column('fullname', Text)

    def __init__(self, id=None, uid=None, username=None, fullname=None):
        self.id = id
        self.uid = uid
        self.username = username
        self.fullname = fullname

    def __repr__(self):
        return "<User('{}', '{}')>".format(self.uid, self.fullname)

    def add(self, uid, username, fullname):
        user = self.get(uid)
        update = {}

        if user:
            if user.username != username:
                update['username'] = username

            if user.fullname != fullname:
                update['fullname'] = fullname

            if update:
                self.update(uid, update)
        else:
            db.add(User(uid=uid,
                        username=username,
                        fullname=fullname))
            db.commit()

        cache.set('user_'.format(uid), User(uid=uid,
                                            username=username,
                                            fullname=fullname))

    @staticmethod
    def get(uid):
        cached = cache.get('user_{}'.format(uid))

        if cached:
            return cached
        else:
            q = db.query(User) \
                .filter(User.uid == uid) \
                .limit(1) \
                .all()
            if q:
                cache.set('user_{}'.format(uid), q[0])
                return q[0]
            else:
                return False

    @staticmethod
    def update(uid, update):
        user = db.query(User).filter(User.uid == uid)
        user.update(update)
        db.commit()


class Chat(Base):
    __tablename__ = 'chats'

    id = Column('id', Integer, primary_key=True)
    cid = Column('cid', BigInteger)
    title = Column('title', Text)

    def __init__(self, id=None, cid=None, title=None):
        self.id = id
        self.cid = cid
        self.title = title

    def __repr__(self):
        return "<Chat('{}', '{}')>".format(self.cid, self.title)

    def add(self, cid, title):
        chat = self.get(cid)

        if chat:
            if chat.title != title:
                self.update(cid, {'title': title})
        else:
            db.add(Chat(cid=cid,
                        title=title))

        cache.set('chat_{}'.format(cid),
                  Chat(cid=cid, title=title))
        db.commit()

    @staticmethod
    def get(cid):
        cached = cache.get('chat_{}'.format(cid))

        if cached:
            return cached
        else:
            q = db.query(Chat) \
                .filter(Chat.cid == cid) \
                .order_by(Chat.id.desc()) \
                .limit(1) \
                .all()
            if q:
                cache.set('chat_{}'.format(cid), q[0])
                return q[0]
            else:
                return False

    @staticmethod
    def update(cid, update):
        chat = db.query(Chat).filter(Chat.cid == cid)
        chat.update(update)
        db.commit()


class Entity(Base):
    __tablename__ = 'entities'

    id = Column('id', Integer, primary_key=True)
    cid = Column('cid', BigInteger)
    type = Column('type', String(20))
    title = Column('title', Text)
    count = Column('count', Integer)

    def __init__(self, id=None, cid=None, type=None, title=None, count=None):
        self.id = id
        self.cid = cid
        self.type = type
        self.title = title
        self.count = count

    def __repr__(self):
        return "<Entity('{}', '{}', '{}', '{}')>".format(self.cid,
                                                         self.type,
                                                         self.title,
                                                         self.count)

    def add(self, cid, type, title):
        entity = self.get(cid, type, title)

        if entity:
            self.update(cid, type, title, {'count': int(entity.count) + 1})
        else:
            db.add(Entity(cid=cid,
                          type=type,
                          title=title,
                          count=1))
        db.commit()

    @staticmethod
    def get(cid, type, title):
        q = db.query(Entity) \
            .filter(Entity.cid == cid,
                    Entity.type == type,
                    Entity.title == title) \
            .limit(1) \
            .all()
        if q:
            return q[0]
        else:
            return False

    @staticmethod
    def update(cid, type, title, update):
        entity = db.query(Entity).filter(Entity.cid == cid,
                                         Entity.type == type,
                                         Entity.title == title)
        entity.update(update)
        db.commit()

    @staticmethod
    def update_all(cid, update):
        entity = db.query(Entity).filter(Entity.cid == cid)

        entity.update(update)
        db.commit()


class UserStat(Base):
    __tablename__ = 'user_stats'

    id = Column('id', Integer, primary_key=True)
    uid = Column('uid', Integer)
    cid = Column('cid', BigInteger)
    msg_count = Column('msg_count', Integer, default=0)
    last_activity = Column('last_activity', Integer)

    def __init__(self, id=None, uid=None, cid=None, msg_count=None, last_activity=None):
        self.id = id
        self.uid = uid
        self.cid = cid
        self.msg_count = msg_count
        self.last_activity = last_activity

    def __repr__(self):
        return "<UserStat('{}', '{}', '{}')>".format(self.cid, self.uid, self.msg_count)

    def add(self, uid, cid, msg_count=1):
        user_stat = self.get(uid, cid)

        if user_stat:
            self.update(uid, cid, {'msg_count': int(user_stat.msg_count) + msg_count,
                                   'last_activity': int(time.time())})
            cache.set('ustat_{}_{}'.format(uid, cid), UserStat(uid=uid,
                                                               cid=cid,
                                                               msg_count=int(user_stat.msg_count) + msg_count,
                                                               last_activity=int(time.time())))
        else:
            c = UserStat(uid=uid,
                         cid=cid,
                         msg_count=msg_count,
                         last_activity=int(time.time()))
            db.add(c)
            cache.set('ustat_{}_{}'.format(uid, cid), c)

        db.commit()

    @staticmethod
    def get(uid, cid):
        cached = cache.get('ustat_{}_{}'.format(uid, cid))

        if cached:
            return cached
        else:
            q = db.query(UserStat) \
                .filter(UserStat.cid == cid,
                        UserStat.uid == uid) \
                .limit(1) \
                .all()
            if q:
                cache.set('ustat_{}_{}'.format(uid, cid), q[0])
                return q[0]
            else:
                return False

    @staticmethod
    def update(uid, cid, update):
        user_stat = db.query(UserStat).filter(UserStat.cid == cid,
                                              UserStat.uid == uid)
        user_stat.update(update)
        db.commit()


class ChatStat(Base):
    __tablename__ = 'chat_stats'

    id = Column('id', Integer, primary_key=True)
    cid = Column('cid', BigInteger)
    users_count = Column('users_count', Integer, default=0)
    msg_count = Column('msg_count', Integer, default=0)
    last_time = Column('last_time', Integer)

    def __init__(self, id=None, cid=None, users_count=None, msg_count=None, last_time=None):
        self.id = id
        self.cid = cid
        self.users_count = users_count
        self.msg_count = msg_count
        self.last_time = last_time

    def __repr__(self):
        return "<ChatStat('{}', '{}')>".format(self.cid, self.msg_count)

    def add(self, cid, users_count, msg_count, last_time):
        chat_stat = self.get(cid)
        today = datetime.today().day

        if chat_stat:
            last_day = datetime.fromtimestamp(timestamp=chat_stat.last_time).day

            c = ChatStat(cid=cid, msg_count=int(chat_stat.msg_count) + msg_count,
                         users_count=int(chat_stat.users_count) + users_count,
                         last_time=last_time)

            if (timedelta(today).days - timedelta(last_day).days) != 0:
                c = ChatStat(cid=cid, msg_count=int(chat_stat.msg_count) + msg_count,
                             users_count=0,
                             last_time=last_time)
                db.add(c)
            else:
                self.update(cid, {'msg_count': int(chat_stat.msg_count) + msg_count,
                                  'users_count': int(chat_stat.users_count) + users_count,
                                  'last_time': last_time})
        else:
            c = ChatStat(cid=cid,
                         msg_count=msg_count,
                         users_count=users_count,
                         last_time=last_time)
            db.add(c)

        cache.set('cstat_{}'.format(cid), c)
        db.commit()

    @staticmethod
    def get(cid):
        cached = cache.get('cstat_{}'.format(cid))

        if cached:
            return cached
        else:
            q = db.query(ChatStat) \
                .filter(ChatStat.cid == cid) \
                .order_by(ChatStat.id.desc()) \
                .limit(1) \
                .all()
            if q:
                cache.set('cstat_{}'.format(cid), q[0])
                return q[0]
            else:
                return False

    @staticmethod
    def update(cid, update):
        sq = db.query(ChatStat.id) \
            .filter(ChatStat.cid == cid) \
            .order_by(ChatStat.id.desc()).limit(1).all()

        db.query(ChatStat) \
            .filter(ChatStat.id == sq[0][0]) \
            .update(update)
        db.commit()


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
                           last_time=int(time.time()))

        cids_list.clear()

    def clear(self):
        self.stack.clear()


class Stats:
    def get_user(self, user_id, chat_id=None):
        all_msg_count = 0
        groups = []

        # All messages
        q = db.query(UserStat).filter(UserStat.uid == user_id).all()
        if q:
            for row in q:
                all_msg_count += row.msg_count
                groups.append(row.cid)

        if chat_id:
            user = UserStat().get(user_id, chat_id)
            if user:
                return {
                    'msg_count': all_msg_count,
                    'group_msg_count': user.msg_count,
                    'percent': self.number_format(user.msg_count * 100 / all_msg_count, 2)
                }

        return {
            'msg_count': all_msg_count,
            'groups': groups
        }

    def get_chat(self, chat_id):
        all_msg_count = 0
        current_users = 0
        top_users = ''
        popular_links = ''

        # All messages in group and active users
        q = db.query(ChatStat) \
            .filter(ChatStat.cid == chat_id) \
            .order_by(ChatStat.id.desc()) \
            .all()
        if q:
            for row in q:
                all_msg_count += row.msg_count
            current_users = q[0].users_count

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
                    top_users += ' *{}. {}* — {} ({}%)\n'.format(i, user.fullname,
                                                                 stats.msg_count,
                                                                 self.number_format(
                                                                     stats.msg_count * 100 / all_msg_count,
                                                                     2))
                else:
                    top_users += ' *{}. {}* — {}\n'.format(i, user.fullname,
                                                           stats.msg_count)

        # Top links generation
        q = db.query(Entity) \
            .filter(Entity.cid == chat_id,
                    Entity.type == 'url') \
            .order_by(Entity.count.desc()) \
            .limit(3) \
            .all()
        if q:
            i = 0
            for url in q:
                i += 1
                popular_links += ' *{}. {}* — {}\n'.format(i, url.title,
                                                           url.count)
        return {
            'msg_count': all_msg_count,
            'current_users': current_users,
            'top_users': top_users,
            'popular_links': popular_links
        }

    @staticmethod
    def number_format(num, places=0):
        return locale.format("%.*f", (places, num), True)

    @staticmethod
    def me_format(fullname, username, group_msg_count, percent, msg_count):
        uname = ''
        if username is not '':
            uname = ' (@{})'.format(username)

        msg = '{}{}:\n' \
              ' Сообщений в этом чате: {} ({}%)\n' \
              ' Сообщений всего: {}'.format(fullname,
                                            uname,
                                            group_msg_count,
                                            percent,
                                            msg_count)
        return msg


engine = create_engine(CONFIG['database'], convert_unicode=True, echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
db = session

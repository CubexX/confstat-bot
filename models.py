# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE
import time
from datetime import datetime

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

        if user:
            return user
        else:
            db.add(User(uid=uid,
                        username=username,
                        fullname=fullname))
            db.commit()

            return User(uid=uid,
                        username=username,
                        fullname=fullname)

    @staticmethod
    def get(uid):
        q = db.query(User).filter(User.uid == uid).all()

        if q:
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
    cid = Column('cid', Integer)
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
        db.commit()

    @staticmethod
    def get(cid):
        q = db.query(Chat).filter(Chat.cid == cid).all()
        if q:
            return q[0]
        else:
            return False

    @staticmethod
    def update(cid, update):
        entity = db.query(Chat).filter(Chat.cid == cid)
        entity.update(update)
        db.commit()


class Entity(Base):
    __tablename__ = 'entities'

    id = Column('id', Integer, primary_key=True)
    cid = Column('cid', Integer)
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
        q = db.query(Entity).filter(Entity.cid == cid,
                                    Entity.type == type,
                                    Entity.title == title).all()
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


class UserStat(Base):
    __tablename__ = 'user_stats'

    id = Column('id', Integer, primary_key=True)
    uid = Column('uid', Integer)
    cid = Column('cid', Integer)
    msg_count = Column('msg_count', Integer, default=0)

    def __init__(self, id=None, uid=None, cid=None, msg_count=None):
        self.id = id
        self.uid = uid
        self.cid = cid
        self.msg_count = msg_count

    def __repr__(self):
        return "<UserStat('{}', '{}', '{}')>".format(self.cid, self.uid, self.msg_count)

    def add(self, uid, cid, msg_count):
        user_stat = self.get(uid, cid)

        if user_stat:
            self.update(uid, cid, int(user_stat.msg_count) + msg_count)
        else:
            db.add(UserStat(uid=uid,
                            cid=cid,
                            msg_count=1))
        db.commit()

    @staticmethod
    def get(uid, cid):
        q = db.query(UserStat).filter(UserStat.cid == cid,
                                      UserStat.uid == uid).all()
        if q:
            return q[0]
        else:
            return False

    @staticmethod
    def update(uid, cid, msg_count):
        user_stat = db.query(UserStat).filter(UserStat.cid == cid,
                                              UserStat.uid == uid)
        user_stat.update({'msg_count': msg_count})
        db.commit()


class ChatStat(Base):
    __tablename__ = 'chat_stats'

    id = Column('id', Integer, primary_key=True)
    cid = Column('cid', Integer)
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

            if last_day < today:
                self.add(cid, msg_count=int(chat_stat.msg_count) + msg_count,
                         users_count=int(chat_stat.users_count) + users_count,
                         last_time=last_time)
            else:
                self.update(cid, msg_count=int(chat_stat.msg_count) + msg_count,
                            users_count=int(chat_stat.users_count) + users_count,
                            last_time=last_time)
        else:
            db.add(ChatStat(cid=cid,
                            msg_count=msg_count,
                            users_count=users_count,
                            last_time=last_time))

        db.commit()

    @staticmethod
    def get(cid):
        q = db.query(ChatStat) \
            .filter(ChatStat.cid == cid) \
            .order_by(ChatStat.id.desc()) \
            .limit(1) \
            .all()
        if q:
            return q[0]
        else:
            return False

    @staticmethod
    def update(cid, users_count, msg_count, last_time):
        chat_stat = db.query(ChatStat).filter(ChatStat.cid == cid)
        chat_stat.update({'msg_count': msg_count,
                          'users_count': users_count,
                          'last_time': last_time})
        db.commit()


class Stack:
    stack = []

    def add(self, obj):
        self.stack.append(obj)

    def send(self):
        cids_list = self.stack

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


engine = create_engine(DATABASE, convert_unicode=True, echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
db = session

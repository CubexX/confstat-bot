# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from sqlalchemy import Column, Integer, Text, Boolean
from Crypto.Hash import MD5
from config import CONFIG
from . import Base
from main import make_db_session
from confstat import cache
import time


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    uid = Column('uid', Integer)
    username = Column('username', Text)
    fullname = Column('fullname', Text)
    public = Column('public', Boolean, default=False)

    def __init__(self, id=None, uid=None, username=None, fullname=None, public=None):
        self.id = id
        self.uid = uid
        self.username = username
        self.fullname = fullname
        self.public = public

    def __repr__(self):
        return "<User('{}', '{}')>".format(self.uid, self.fullname)

    @make_db_session
    def add(self, uid, username, fullname, db):
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
        cache.delete('web_user_{}'.format(uid))

    @staticmethod
    @make_db_session
    def get(uid, db):
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
                cache.delete('web_user_{}'.format(uid))
                return q[0]
            else:
                return False

    @staticmethod
    @make_db_session
    def update(uid, update, db):
        user = db.query(User).filter(User.uid == uid)
        user.update(update)
        db.commit()

    @staticmethod
    def generate_token(uid):
        salt = str(CONFIG['salt']).encode('utf-8')
        current_time = str(time.time()).encode('utf-8')
        uid = str(uid).encode('utf-8')

        t = MD5.new(uid)
        t.update(salt)
        t.update(current_time)
        token = t.hexdigest()[:8]

        return token

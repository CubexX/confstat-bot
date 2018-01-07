# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from sqlalchemy import Column, Integer, BigInteger
from confstat.models import Base
from main import make_db_session
from confstat import cache
import time


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

    @make_db_session
    def add(self, uid, cid, db, msg_count=1):
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
    @make_db_session
    def get(uid, cid, db):
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
    @make_db_session
    def update(uid, cid, update, db):
        user_stat = db.query(UserStat).filter(UserStat.cid == cid,
                                              UserStat.uid == uid)
        user_stat.update(update)
        db.commit()

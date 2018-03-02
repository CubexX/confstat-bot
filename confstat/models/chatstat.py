# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from datetime import datetime, timedelta

from sqlalchemy import BigInteger, Column, Integer

from confstat import cache
from confstat.models import Base
from main import make_db_session


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

    @make_db_session
    def add(self, cid, users_count, msg_count, last_time, db):
        chat_stat = self.get(cid)
        today = datetime.today().day

        if chat_stat:
            last_day = datetime.fromtimestamp(chat_stat.last_time).day

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
    @make_db_session
    def get(cid, db):
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
    @make_db_session
    def update(cid, update, db):
        sq = db.query(ChatStat.id) \
            .filter(ChatStat.cid == cid) \
            .order_by(ChatStat.id.desc()).limit(1).all()

        db.query(ChatStat) \
            .filter(ChatStat.id == sq[0][0]) \
            .update(update)
        db.commit()

    @staticmethod
    @make_db_session
    def update_all(old_id, new_id, db):
        for c in db.query(ChatStat) \
                .filter(ChatStat.cid == old_id) \
                .all():
            c.cid = new_id
        db.commit()

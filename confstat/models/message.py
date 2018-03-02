# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from time import time

from sqlalchemy import BigInteger, Column, Integer

from main import make_db_session

from . import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column('id', Integer, primary_key=True)
    uid = Column('uid', Integer)
    cid = Column('cid', BigInteger)
    date = Column('date', Integer)

    def __init__(self, id=None, uid=None, cid=None, date=None):
        self.id = id
        self.uid = uid
        self.cid = cid
        self.date = date

    def __repr__(self):
        return "<Msg('{}', '{}', '{}')>".format(self.uid, self.cid, self.date)

    @make_db_session
    def add(self, uid, cid, db):
        db.add(
            Message(
                uid=uid,
                cid=cid,
                date=int(time())
            )
        )
        db.commit()

    @staticmethod
    @make_db_session
    def update_all(old_id, new_id, db):
        for c in db.query(Message) \
                .filter(Message.cid == old_id) \
                .all():
            c.cid = new_id
        db.commit()

# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from sqlalchemy import Column, Integer, Text, BigInteger
from . import Base
from main import make_db_session
from confstat import cache


class Chat(Base):
    __tablename__ = 'chats'

    id = Column('id', Integer, primary_key=True)
    cid = Column('cid', BigInteger)
    title = Column('title', Text)
    public_link = Column('public_link', Text)

    def __init__(self, id=None, cid=None, title=None, public_link=None):
        self.id = id
        self.cid = cid
        self.title = title
        self.public_link = public_link

    def __repr__(self):
        return "<Chat('{}', '{}')>".format(self.cid, self.title)

    @make_db_session
    def add(self, cid, title, db, public_link=''):
        chat = self.get(cid)

        if chat:
            if chat.title != title:
                self.update(cid, {'title': title})

            if chat.public_link != public_link:
                self.update(cid, {'public_link': public_link})
        else:
            db.add(Chat(cid=cid,
                        title=title,
                        public_link=public_link))

        cache.set('chat_{}'.format(cid),
                  Chat(cid=cid, title=title))
        cache.delete('web_chat_{}'.format(cid))
        db.commit()

    @staticmethod
    @make_db_session
    def get(cid, db):
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
                cache.delete('web_chat_{}'.format(cid))
                return q[0]
            else:
                return False

    @staticmethod
    @make_db_session
    def update(cid, update, db):
        chat = db.query(Chat).filter(Chat.cid == cid)
        chat.update(update)
        db.commit()

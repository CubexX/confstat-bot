# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from Crypto.Hash import MD5
from config import CONFIG
from time import time
from sqlalchemy import BigInteger, Column, Integer, Text

from confstat import cache
from main import make_db_session

from . import Base


class Chat(Base):
    __tablename__ = 'chats'

    id = Column('id', Integer, primary_key=True)
    cid = Column('cid', BigInteger)
    title = Column('title', Text)
    public_link = Column('public_link', Text)
    add_time = Column('add_time', Integer)
    chat_hash = Column('hash', Text)

    def __init__(self, id=None, cid=None, title=None, public_link=None, add_time=None, chat_hash=None):
        self.id = id
        self.cid = cid
        self.title = title
        self.public_link = public_link
        self.add_time = add_time
        self.chat_hash = chat_hash

    def __repr__(self):
        return "<Chat('{}', '{}')>".format(self.cid, self.title)

    @make_db_session
    def add(self, cid, title, db, public_link=''):
        chat = self.get(cid)
        add_time = round(time())

        if chat:
            if chat.title != title:
                self.update(cid, {'title': title})

            if chat.public_link != public_link:
                self.update(cid, {'public_link': public_link})
        else:
            # Statistics for admin panel
            c = cache.get('today_chats')

            if c:
                cache.incr('today_chats')
            else:
                cache.set('today_chats', 1, 86400)

            # Add new chat to database
            db.add(Chat(cid=cid,
                        title=title,
                        public_link=public_link,
                        add_time=add_time,
                        chat_hash=self.generate_hash(cid)))

        # Add new/updated chat to memcache
        cache.set('chat_{}'.format(cid),
                  Chat(cid=cid,
                       title=title,
                       public_link=public_link,
                       add_time=add_time,
                       chat_hash=self.generate_hash(cid)))

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

    @staticmethod
    def generate_hash(cid):
        salt = str(CONFIG['salt']).encode('utf-8')
        cid = str(cid).encode('utf-8')

        h = MD5.new(cid)
        h.update(salt)
        chat_hash = h.hexdigest()

        return chat_hash

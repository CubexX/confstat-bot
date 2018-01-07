# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from sqlalchemy import Column, Integer, Text, BigInteger, String
from main import make_db_session
from . import Base


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
        return "<Entity('{}', '{}', '{}')>".format(self.type, self.title, self.count)

    @make_db_session
    def add(self, cid, type, title, db):
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
    @make_db_session
    def get(cid, type, title, db):
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
    @make_db_session
    def update(cid, type, title, update, db):
        entity = db.query(Entity).filter(Entity.cid == cid,
                                         Entity.type == type,
                                         Entity.title == title)
        entity.update(update)
        db.commit()

    @staticmethod
    @make_db_session
    def update_all(cid, update, db):
        entity = db.query(Entity).filter(Entity.cid == cid)

        entity.update(update)
        db.commit()

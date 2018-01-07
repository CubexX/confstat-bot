# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def make_session_maker(url):
    engine = create_engine(url, convert_unicode=True, echo=False)
    return sessionmaker(bind=engine)

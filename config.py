# -*- coding: utf-8 -*-
__author__ = 'CubexX'

import logging
import memcache

TOKEN = ""
DATABASE = 'mysql://user:pass@localhost/table'
SITE_URL = ''

cache = memcache.Client(['127.0.0.1:11211'], debug=1)

logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] - %(message)s',
    level=logging.INFO,
    # filename='bot.log'
)
logger = logging.getLogger(__name__)

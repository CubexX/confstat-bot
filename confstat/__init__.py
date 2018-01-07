# -*- coding: utf-8 -*-
__author__ = 'CubexX'

import memcache

from . import models
from config import CONFIG

cache = memcache.Client(CONFIG['cache']['servers'], debug=CONFIG['cache']['debug'])

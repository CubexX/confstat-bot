# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from . import models
import memcache
from config import CONFIG

cache = memcache.Client(CONFIG['cache']['servers'], debug=CONFIG['cache']['debug'])

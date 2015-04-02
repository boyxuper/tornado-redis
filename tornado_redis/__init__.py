#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 10:41'


import redis
from tornado import version_info

if version_info[0] >= 4:
    from .tornado4 import TornadoExecutor
else:
    from .tornado2x3x import TornadoExecutor


class StrictTornadoRedis(TornadoExecutor, redis.StrictRedis):
    pass


class TornadoRedis(TornadoExecutor, redis.Redis):
    pass

del version_info, TornadoExecutor


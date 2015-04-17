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
    def __init__(self, *args, **kwargs):
        redis.StrictRedis.__init__(self, *args, **kwargs)


class TornadoRedis(TornadoExecutor, redis.Redis):
    def __init__(self, *args, **kwargs):
        redis.Redis.__init__(self, *args, **kwargs)

del version_info, TornadoExecutor


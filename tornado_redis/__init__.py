#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 10:41'


from tornado import version_info

if version_info[0] >= 4:
    from .tornado2x3x import TornadoRedis
else:
    from .tornado4 import TornadoRedis

del version_info


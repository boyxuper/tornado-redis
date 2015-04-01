#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 11:03'


from tornado import ioloop, gen, web
from tornado_redis import TornadoRedis


client = TornadoRedis()


class IndexHandler(web.RequestHandler):
    @web.asynchronous
    @gen.engine
    def get(self, *args, **kwargs):
        result = yield [client.mget('a', 'b', 'c'), ]
        self.finish(repr(result))


app = web.Application([
    ('/', IndexHandler),
])

app.listen(8080)

ioloop = ioloop.IOLoop.instance()
ioloop.start()

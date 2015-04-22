#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 10:47'


import time

import redis
from tornado import gen, concurrent, ioloop


class TornadoExecutor(object):
    @gen.coroutine
    def execute_command(self, *args, **options):
        ioloop_obj = ioloop.IOLoop.instance()
        pool = self.connection_pool
        command_name = args[0]
        conn = pool.get_connection(command_name, **options)

        try:
            # ensure fd
            conn.connect()
            # early send
            conn.send_command(*args)
        except:
            pool.release(conn)
            raise

        conn_fd = conn._sock.fileno()
        read_future = concurrent.Future()

        try:
            ioloop_obj.add_handler(
                conn_fd,
                lambda fd, event: read_future.set_result(event),
                ioloop.IOLoop.READ | ioloop.IOLoop.ERROR)

            _timeout = None
            if conn.socket_timeout:
                _timeout = ioloop_obj.add_timeout(
                    time.time() + conn.socket_timeout,
                    lambda: read_future.set_result(False))

            ready = yield read_future
            if ready is False:
                raise redis.TimeoutError("Timeout while waiting socket to be ready for read.")

            if _timeout:
                ioloop_obj.remove_timeout(_timeout)
            ioloop_obj.remove_handler(conn_fd)

            result = self.parse_response(conn, command_name, **options)
        finally:
            pool.release(conn)

        raise gen.Return(result)

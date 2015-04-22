#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 10:46'


import time

import redis
from tornado import gen, ioloop


class TornadoExecutor(object):
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

        @gen.engine
        def _task(callback):
            try:
                wait_callback = yield gen.Callback(conn)
                conn_fd = conn._sock.fileno()

                ioloop_obj.add_handler(
                    conn_fd, lambda fd, event: wait_callback(event),
                    ioloop.IOLoop.READ | ioloop.IOLoop.ERROR)

                _timeout = False
                if conn.socket_timeout:
                    _timeout = ioloop_obj.add_handler(
                        time.time() + conn.socket_timeout, lambda: wait_callback(False))

                ready = yield gen.Wait(conn)
                if ready is False:
                    raise redis.TimeoutError("Timeout while waiting socket to be ready for read.")

                ioloop_obj.remove_handler(conn_fd)
                if _timeout:
                    ioloop_obj.remove_timeout(_timeout)

                result = self.parse_response(conn, command_name, **options)
                callback(result)
            finally:
                pool.release(conn)

        return gen.Task(_task)

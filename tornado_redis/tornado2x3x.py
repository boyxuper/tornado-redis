#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 10:46'


import functools

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
                conn_fd = conn._sock.fileno()
                handler = functools.partial(
                    lambda fd, event, continue_fn: continue_fn(event),
                    continue_fn=(yield gen.Callback(conn)))
                ioloop_obj.add_handler(conn_fd, handler, ioloop.IOLoop.READ | ioloop.IOLoop.ERROR)

                yield gen.Wait(conn)
                ioloop_obj.remove_handler(conn_fd)

                result = self.parse_response(conn, command_name, **options)
                callback(result)
            finally:
                pool.release(conn)

        return gen.Task(_task)

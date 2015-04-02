#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 10:47'


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

            yield read_future
            ioloop_obj.remove_handler(conn_fd)
            result = self.parse_response(conn, command_name, **options)
        finally:
            pool.release(conn)

        raise gen.Return(result)

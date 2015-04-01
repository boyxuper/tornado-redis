#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnxu'
__date__ = '2015/4/1 10:47'

from redis import StrictRedis
from tornado import gen, concurrent, ioloop


class TornadoRedis(StrictRedis):
    @gen.coroutine
    def execute_command(self, *args, **options):
        ioloop_obj = ioloop.IOLoop.instance()
        pool = self.connection_pool
        command_name = args[0]
        connection = pool.get_connection(command_name, **options)

        try:
            # ensure fd
            connection.connect()
            # early send
            connection.send_command(*args)
        except:
            pool.release(connection)
            raise

        connection_fd = connection._sock.fileno()
        read_future = concurrent.Future()

        try:
            ioloop_obj.add_handler(
                connection_fd,
                lambda fd, event: read_future.set_result(event),
                ioloop.IOLoop.READ | ioloop.IOLoop.ERROR)

            yield read_future
            ioloop_obj.remove_handler(connection_fd)
            result = self.parse_response(connection, command_name, **options)
        finally:
            pool.release(connection)

        raise gen.Return(result)
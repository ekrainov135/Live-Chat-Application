import asyncio
import socket
from abc import ABC, abstractmethod

from settings import server_logger
from core.transport import TransportTCP


class SocketManager(ABC):
    """ Base class of a low-level tcp-server """

    def __init__(self, transport=TransportTCP, *args, **kwargs):
        self._transport = TransportTCP
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._loop = asyncio.new_event_loop()

        self.is_active = False

    def start(self, host, port, tasks_count=1, queue_length=5):
        """ Sets up a port listener and starts tasks to listen for incoming connections in an event loop.  """

        self._socket.bind((host, int(port)))
        self._socket.listen(queue_length)

        self.is_active = True
        server_logger.info(f'Server start {host}:{port}')

        task_list = [self._echo() for _ in range(tasks_count)]
        self._loop.run_until_complete(asyncio.wait(task_list))

    async def _echo(self):
        """ Creates tasks for processing incoming connections asynchronously.  """

        while self.is_active:
            try:
                connection, address = await self._loop.run_in_executor(None, self._socket.accept)
            except OSError as e:
                break
            self._loop.create_task(self._connection_handle(connection, address))

    async def _connection_handle(self, connection, address):
        """ Wrapper connection_handle method for correct connection handling.  """

        with self._transport(connection, address) as transport:
            try:
                await self.connection_handle(transport)
            except ConnectionError as e:
                transport.close()

    async def connection_handle(self, transport):
        """ Handles incoming TransportTCP connection.  """

        return

    def stop(self):
        server_logger.info(f'Server stop')
        self.is_active = False

        self._socket.close()

    def abort(self):
        server_logger.warning('server socket abort')
        self.stop()
        self._loop.stop()


class ServerError(Exception):
    pass

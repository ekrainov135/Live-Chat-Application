import asyncio
import json
import socket
import time
from abc import ABC, abstractmethod

from settings import server_logger
from core.storage import ChatDriverJSON, ChatStorageDriver
from core.transport import TransportTCP


class SocketManager(ABC):
    """ Base class of a low-level tcp-server """

    def __init__(self, *args, **kwargs):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._loop = asyncio.new_event_loop()

        self.is_active = False
        self.receivers = {}

    def start(self, host, port, tasks_count=1, queue_length=5):
        """ Sets up a port listener and starts tasks to listen for incoming connections in an event loop.  """

        self._socket.bind((host, int(port)))
        self._socket.listen(int(queue_length))

        self.is_active = True
        server_logger.info(f'Server start {host}:{port}')

        task_list = [self._echo() for _ in range(tasks_count)]
        self._loop.run_until_complete(asyncio.wait(task_list))

    async def _echo(self):
        while self.is_active:
            try:
                connection, address = await self._loop.run_in_executor(None, self._socket.accept)
            except OSError as e:
                break
            else:
                self._loop.create_task(self._connection_handle(connection, address))

    async def _connection_handle(self, connection, address):
        """ Wrapper connection_handle method for correct connection handling.  """

        with TransportTCP(connection, address) as transport:
            try:
                await self.connection_handle(transport)
            except ConnectionError as e:
                transport.close()

    async def connection_handle(self, transport):
        return

    def stop(self):
        server_logger.info(f'Server stop')
        self.is_active = False

        self._socket.close()

    def abort(self):
        server_logger.warning('server socket abort')
        self.stop()
        self._loop.stop()


class ChatSocketManager(SocketManager):
    """ Chat manager class. Processes requests from the client and stores the chat history in json.  """

    def _login_required(func):
        """ Decorator for functions using login.  """

        async def wrapped(self, transport, data_json):
            is_identified = transport.fileno in self.members
            is_authenticated = is_identified and self.members[transport.fileno].username == data_json['username']

            return await func(self, transport, data_json) if is_identified and is_authenticated else None
        return wrapped

    def __init__(self, storage_driver=ChatDriverJSON, storage_connection='storage.json', *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize driver to access the chat storage history
        if storage_driver is not None and not issubclass(storage_driver, ChatStorageDriver):
            raise TypeError
        self.storage = storage_driver(storage_connection)

        # Protocol method handlers
        self.receivers = {'login': self._transport_login, 'logout': self._transport_logout, 'send': self._transport_send}

        # Chat member dictionary in the format: {<member fileno>: <member transport>}
        # Also the username is stored in <member writer> value
        self.members = {}

    async def connection_handle(self, transport):
        try:
            # Waiting for authentication data from client
            data_json = transport.read()
            if data_json['type'] != 'login':
                return
            await self._transport_login(transport, data_json)

            # Sending chat history
            chat_history_response = {'type': 'send', 'content': self.storage.objects}
            transport.write(chat_history_response)

            # Listening to incoming messages from the client
            while self.is_active:
                data_json = await self._loop.run_in_executor(None, transport.read)
                await self.receivers[data_json['type']](transport, data_json)

        except ConnectionError as e:
            if transport.fileno in self.members:
                server_logger.warning(f'forcibly disconnection: {transport.peername}')
                await self._transport_logout(transport)

    def stop(self):
        self.storage.close()
        for member_transport in self.members.values():
            member_transport.close()
        super().stop()

    async def _transport_login(self, transport, data_json):
        is_occupied = data_json['username'] in [writer.username for writer in self.members.values()]

        # Sending a response to the user
        data_json['status'] = 'this username is already taken' if is_occupied else 'ok'
        transport.write(data_json)

        if is_occupied:
            await self._transport_logout(transport)
        else:
            transport.username = data_json['username']
            self.members[transport.fileno] = transport

            server_logger.info(f"connected client: {transport.peername} as '{data_json.get('username')}'")

    async def _transport_logout(self, transport, data_json=None):
        if transport.peername in self.members:
            self.members.pop(transport.peername)

        transport.close()

        server_logger.info(f"disconnected client: {transport.peername}")

    @_login_required
    async def _transport_send(self, transport, data_json):
        self.storage.send(data_json['username'], data_json['content'])

        # A new message is sent as a list
        data_json['content'] = self.storage.objects[-1:]
        for transport in self.members.values():
            transport.write(data_json)


class ServerError(Exception):
    pass

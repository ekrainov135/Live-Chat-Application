
import asyncio
import json
from abc import ABC, abstractmethod

from core.services import ChatStorageDriver


class BaseServerManager(ABC):
    """ Base class of a low-level tcp-server """

    async def read(self, reader):
        data_text = await reader.read(1024)
        return json.loads(data_text.decode())

    def write(self, writer, data_json):
        response = json.dumps(data_json)
        writer.write(response.encode()+b'\n')

    def start(self, host='127.0.0.1', port=7070):
        self._loop = asyncio.get_event_loop()
        self._coro = asyncio.start_server(self.connection_handle, host, int(port), loop=self._loop)
        self.server = self._loop.run_until_complete(self._coro)
        self._loop.run_forever()

    def close(self):
        self.server.close()
        self._loop.run_until_complete(self.server.wait_closed())
        self._loop.close()

    @abstractmethod
    async def connection_handle(self, reader, writer):
        pass


class ChatServerManager(BaseServerManager):

    def login_required(func):
        """ Decorator for functions using login.  """

        async def wrapped(self, writer, data_json):
            if writer.get_extra_info('peername') not in self.members:
                return
            return await func(self, writer, data_json)
        return wrapped

    def __init__(self):
        self.storage = ChatStorageDriver('storage.json')

        # Protocol method handlers
        self.handlers = {'login': self.connection_login, 'logout': self.connection_logout, 'send': self.connection_send}

        # Chat member dictionary in the format: {<member peername>: <member writer>}
        # Also the username is stored in <member writer> value
        self.members = {}

    async def connection_handle(self, reader, writer):
        try:
            data_json = await self.read(reader)
            if data_json['type'] != 'login':
                return
            await self.connection_login(writer, data_json)

            response = {'type': 'send',
                        'username': data_json['username'],
                        'content': self.storage.objects
                        }
            self.write(writer, response)

            while True:
                data_json = await self.read(reader)
                await self.handlers[data_json['type']](writer, data_json)

        except (ConnectionError, ChatServerError) as e:
            await self.connection_logout(writer)

    async def connection_login(self, writer, data_json):
        peername = writer.get_extra_info('peername')
        print('connect:', peername)

        is_occupied = data_json['username'] in [writer.username for writer in self.members.values()]

        # Sending a response to the user
        data_json['status'] = 'fail' if is_occupied else 'ok'
        self.write(writer, data_json)

        if is_occupied:
            raise ChatServerError('this username is taken')
        else:
            writer.username = data_json['username']
            self.members[peername] = writer

    async def connection_logout(self, writer, data_json=None):
        peername = writer.get_extra_info('peername')
        print('disconnect:', peername)

        if data_json is not None:
            data_json['status'] = 'ok'
            self.write(writer, data_json)

        if peername in self.members:
            self.members.pop(peername)

        writer.close()
        if not writer.is_closing():
            await writer.wait_closed()

    @login_required
    async def connection_send(self, writer, data_json):
        self.storage.push_message(data_json['username'], data_json['content'])

        # A new message is sent as a list
        data_json['content'] = self.storage.objects[-1:]
        for writer in self.members.values():
            self.write(writer, data_json)


class ChatServerError(Exception):
    pass
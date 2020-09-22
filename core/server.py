
import json
import time
from abc import ABC, abstractmethod

from core.services import ChatStorageDriver


class BaseServerManager(ABC):
    """ Base class of a low-level tcp-server """

    async def read(self, reader):
        data = b''

        while not data.endswith(b'\n'):
            data += await reader.read(1024)
        return json.loads(data.decode())

    def write(self, writer, data_json):
        writer.write(json.dumps(data_json).encode()+b'\n')

    @abstractmethod
    async def connection_handle(self, reader, writer):
        pass


class ChatServerManager(BaseServerManager):

    def login_required(func):
        """ Decorator for functions using login.  """

        async def wrapped(self, writer, data_json):
            peername = writer.get_extra_info('peername')
            is_identified = peername in self.members
            is_authenticated = is_identified and self.members[peername].username == data_json['username']

            return await func(self, writer, data_json) if is_identified and is_authenticated else None
        return wrapped

    def __init__(self):
        self.storage = ChatStorageDriver('storage.json')

        # Protocol method handlers
        self.receivers = {'login': self._transport_login, 'logout': self._transport_logout, 'send': self._transport_send}

        # Chat member dictionary in the format: {<member peername>: <member writer>}
        # Also the username is stored in <member writer> value
        self.members = {}

    async def connection_handle(self, reader, writer):
        try:
            # Waiting for authentication data from client
            data_json = await self.read(reader)
            if data_json['type'] != 'login':
                return
            await self._transport_login(writer, data_json)

            # Sending chat history
            chat_history_response = {'type': 'send', 'content': self.storage.objects}
            self.write(writer, chat_history_response)

            # Listening to incoming messages from the client
            while True:
                data_json = await self.read(reader)
                await self.receivers[data_json['type']](writer, data_json)

        except (ConnectionError, ChatServerError) as e:
            await self._transport_logout(writer)

    async def _transport_login(self, writer, data_json):
        peername = writer.get_extra_info('peername')
        print(f"[{time.strftime('%x %X')}] connect: {peername} as '{data_json.get('username')}'")

        is_occupied = data_json['username'] in [writer.username for writer in self.members.values()]

        # Sending a response to the user
        data_json['status'] = 'this username is already taken' if is_occupied else 'ok'
        self.write(writer, data_json)

        if is_occupied:
            await self._transport_logout(writer)
        else:
            writer.username = data_json['username']
            self.members[peername] = writer

    async def _transport_logout(self, writer, data_json=None):
        peername = writer.get_extra_info('peername')
        print(f"[{time.strftime('%x %X')}] disconnect: {peername}", end=' forcibly\n' if data_json is None else '\n')

        if peername in self.members:
            self.members.pop(peername)

        writer.transport.pause_reading()

    @login_required
    async def _transport_send(self, writer, data_json):
        self.storage.push_message(data_json['username'], data_json['content'])

        # A new message is sent as a list
        data_json['content'] = self.storage.objects[-1:]
        for writer in self.members.values():
            self.write(writer, data_json)


class ChatServerError(Exception):
    pass
import asyncio
import json
import socket


class BaseClient:
    handlers = {}

    def __del__(self):
        self._connection.close()
        del self._connection

    def read(self):
        data = b''

        while not data.endswith(b'\n'):
            try:
                data += self._connection.recv(1024)
            except socket.error as e:
                raise ChatClientError("error reading data from socket", e)

        return data.decode('utf-8')

    def write(self, data):
        try:
            self._connection.send(data.encode("utf8"))
        except socket.error as e:
            raise ChatClientError("error reading data from socket", e)

    def connect(self, host='127.0.0.1', port=7070, timeout=None):
        try:
            self._connection = socket.create_connection((host, int(port)), timeout)
        except socket.error as e:
            raise ChatClientError("cannot create connection", e)

    def echo_server(self):
        while True:
            response = json.loads(self.read())
            self.handlers[response['type']](response)


class ChatClient(BaseClient):

    def __init__(self):
        self.handlers = {'send': self._send}

    def _send(self, data_json):
        for message_object in data_json['content']:
            print(f"({message_object['timestamp']}) {message_object['member']}: {message_object['message']}")

    def authorize(self, username):
        request = {'type': 'login', 'username': username}
        self.write(json.dumps(request))
        response = json.loads(self.read())
        print(response)
        self.username = username
        return response['status'] == 'ok'

    def send(self, message):
        request = {'type': 'send', 'username': self.username, 'content': message}
        self.write(json.dumps(request))


class ChatClientError(Exception):
    pass
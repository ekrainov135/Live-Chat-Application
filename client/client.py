import json
import socket
import time


CLEARING_STRING = "\033[A                             \033[A"


class BaseClient:

    def __init__(self):
        self.is_active = False
        self.handlers = {}

    def __del__(self):
        self._connection.close()
        del self._connection

    def read(self):
        data = b''

        while not data.endswith(b'\n'):
            try:
                data += self._connection.recv(1024)
            except socket.error as e:
                raise ChatClientError("unknown server error", e)

        return json.loads(data.decode())

    def write(self, data_json):
        try:
            self._connection.send(json.dumps(data_json).encode()+b'\n')
        except socket.error as e:
            raise ChatClientError("unknown server error", e)

    def connect(self, host, port, timeout=None):
        try:
            self._connection = socket.create_connection((host, int(port)), timeout)
            self.is_active = True
        except socket.error as e:
            raise ChatClientError("unknown server error", e)

    def disconnect(self):
        self.is_active = False
        self._connection.close()

    def echo_server(self):
        while self.is_active:
            try:
                response = self.read()
                if response['type'] in self.handlers:
                    self.handlers[response['type']](response)
            except (ConnectionError, ChatClientError):
                break


class ChatClient(BaseClient):

    def __init__(self):
        super().__init__()
        self.handlers = {'send': self._send}

    def _send(self, data_json):
        for message_object in data_json['content']:
            print(CLEARING_STRING)
            print(f"({message_object['timestamp']}) {message_object['member']}: {message_object['message']}\n")

    def login(self, username, server=('127.0.0.1', 7070)):
        if not self.is_active:
            self.connect(*server)

        request = {'type': 'login', 'username': username}
        self.write(request)
        response = self.read()
        if response['status'] != 'ok':
            raise ChatClientError(response['status'])
        self.username = username
        
    def logout(self):
        request = {'type': 'logout', 'username': self.username}
        self.write(request)

        # Wait the server closes the connection itself
        # Connection is broken forced if the server did not time to do
        time.sleep(0.2)
        self.disconnect()

    def send(self, message):
        request = {'type': 'send', 'username': self.username, 'content': message}
        self.write(request)


class ChatClientError(Exception):
    pass
import json


class TransportTCP:
    """ Class extension for working with connections.  """

    def __init__(self, connection, address):
        self._connection, self.fileno, self.peername = connection, connection.fileno(), address
        self.char_end = b'\n'

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._connection.close()

    def read(self):
        data = b''

        while not data.endswith(self.char_end):
            try:
                data += self._connection.recv(1024)
            except (ConnectionError, OSError) as e:
                self._connection.close()
                raise ConnectionError(e)

        return json.loads(data.decode())

    def write(self, data_json):
        try:
            self._connection.send(json.dumps(data_json).encode()+self.char_end)
        except (ConnectionError, OSError) as e:
            self._connection.close()
            raise ConnectionError(e)

    def close(self):
        self._connection.close()



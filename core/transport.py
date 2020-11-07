import json


class TransportTCP:
    """ Class extension for working with connections.  """

    def __init__(self, connection, address):
        self._connection, self.fileno, self.peername = connection, connection.fileno(), address
        self.char_end = b'\n'
        self.bufsize = 1024

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._connection.close()

    def read(self):
        result, data = {}, b''

        while not data.endswith(self.char_end):
            try:
                data += self._connection.recv(self.bufsize)
            except (ConnectionError, OSError) as e:
                self._connection.close()
                raise ConnectionError(e)

        try:
            result = json.loads(data.decode())
        except json.JSONDecodeError:
            pass

        return result

    def write(self, data_json):
        try:
            self._connection.send(json.dumps(data_json).encode()+self.char_end)
        except (ConnectionError, OSError) as e:
            self._connection.close()
            raise ConnectionError(e)

    def close(self):
        self._connection.close()



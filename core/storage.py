import json
import time
from abc import ABC, abstractmethod


class BaseStorageDriver(ABC):
    """ Base class storage driver.  """

    _objects = None

    @property
    def objects(self):
        return self._objects

    def close(self):
        pass


class ChatStorageDriver(BaseStorageDriver):
    """ Abstract class with chat interface.  """

    @abstractmethod
    def send(self, username, message):
        pass


class DriverJSON(BaseStorageDriver):
    """ Abstract class for working with json files.  """

    def __init__(self, filename):
        self._filename = filename
        with open(filename) as storage_file:
            data = storage_file.read()
            self._objects = json.loads(data)

    def save(self):
        with open(self._filename, 'w') as storage_file:
            storage_file.write(json.dumps(self._objects, ensure_ascii=False, indent=4))

    def close(self):
        self.save()


class ChatDriverJSON(ChatStorageDriver, DriverJSON):
    TIME_PATTERN = '%A %H:%M'

    def send(self, username, message):
        self._objects.append(
            {
                'member': username,
                'message': message,
                'timestamp': time.strftime(self.TIME_PATTERN)
            })





import json
import time
from abc import ABC, abstractmethod


class BaseStorageDriver(ABC):

    def __init__(self, filename):
        self._filename = filename
        with open(filename) as storage_file:
            data = storage_file.read()
            self._objects = json.loads(data)

    @property
    def objects(self):
        return self._objects

    def save(self):
        with open(self._filename, 'w') as storage_file:
            storage_file.write(json.dumps(self._objects, ensure_ascii=False, indent=4))


class ChatStorageDriver(BaseStorageDriver):
    TIME_PATTERN = '%A %H:%M'

    @property
    def objects(self):
        return self._objects

    def push_message(self, username, message):
        self._objects.append(
            {
                'member': username,
                'message': message,
                'timestamp': time.strftime(self.TIME_PATTERN)
            })
        self.save()





import json
import time
from abc import ABC, abstractmethod


# =====================================================================================================================
# Drivers classes
# =====================================================================================================================

class BaseStorageDriver(ABC):
    """ Base class storage driver.  """


class FileStorageDriver(BaseStorageDriver):
    """ Abstract file storage driver.  """

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, data):
        pass


class DriverJSON(BaseStorageDriver):
    """ Driver for handling json files.  """

    def __init__(self, filename):
        self._filename = filename

    def read(self):
        with open(self._filename) as storage_file:
            data = storage_file.read()
            result = json.loads(data)
        return result

    def write(self, data, mode='w'):
        with open(self._filename, mode) as storage_file:
            storage_file.write(json.dumps(data, ensure_ascii=False, indent=4))


# =====================================================================================================================
# Controllers classes
# =====================================================================================================================

class BaseStorageController(ABC):
    """ Base class storage controller.  """

    _objects = None

    def __init__(self, driver):
        self.driver = driver

    @property
    def objects(self):
        self._objects = self.driver.read()
        return self._objects

    @objects.setter
    def objects(self, objects):
        self._objects = objects
        self.driver.write(self._objects)

    def close(self):
        pass







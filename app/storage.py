import time

from core.storage import BaseStorageController


class ChatStorageController(BaseStorageController):
    """ Chat class storage controller.  """

    TIME_PATTERN = '%A %H:%M'

    def send(self, username, message):
        self._objects.append(
            {
                'member': username,
                'message': message,
                'timestamp': time.strftime(self.TIME_PATTERN)
            })
        self.driver.write(self._objects)

import logging


APP_NAME = 'tcp_server'


# Logging settings

LOG_FILE_PATH = 'server.log'
LOG_TEXT_FORMAT = '%(levelname)s [%(asctime)s] %(name)s: %(message)s'

logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE_PATH, format=LOG_TEXT_FORMAT)

server_logger = logging.getLogger(APP_NAME)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(name)s: %(message)s', '%m.%d %X'))

server_logger.addHandler(stream_handler)

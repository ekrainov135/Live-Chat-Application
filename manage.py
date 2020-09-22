import asyncio
import sys

from core.server import ChatServerManager


def run_chat_server(host='127.0.0.1', port=7070):
    chat_server_manager = ChatServerManager()
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(chat_server_manager.connection_handle, host, int(port), loop=loop)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


def main():
    COMMAND_DEFAULT = 'run_chat_server'
    console_command = COMMAND_DEFAULT if len(sys.argv) == 1 else sys.argv[1]
    if console_command == 'run_chat_server':
        run_chat_server('127.0.0.1', 7070)
    else:
        pass


if __name__ == '__main__':
    main()




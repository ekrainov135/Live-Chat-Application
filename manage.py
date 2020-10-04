import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import settings
from core.server import ChatSocketManager


def run_chat_server(host='127.0.0.1', port=7070):
    chat_socket = ChatSocketManager()

    loop = asyncio.get_event_loop()
    loop.create_task(server_input(loop, chat_socket))

    with ThreadPoolExecutor() as pool:
        loop.run_until_complete(loop.run_in_executor(pool, chat_socket.start, host, port))


async def server_input(loop, server):
    """ Function to manage the server from the console.  """

    commands = {'stop': server.stop, 'abort': server.abort,
                'clear': lambda: os.system('cls' if os.name == 'nt' else 'clear'),
                }

    while True:
        cmd, *args = (await loop.run_in_executor(None, input)).split()
        if cmd in ('stop', 'abort'):
            commands[cmd]()
            break
        elif cmd in commands:
            commands[cmd](*args)


def main():
    COMMAND_DEFAULT = 'run_chat_server'
    console_command = COMMAND_DEFAULT if len(sys.argv) == 1 else sys.argv[1]
    if console_command == 'run_chat_server':
        run_chat_server('127.0.0.1', 7070)
    else:
        pass


if __name__ == '__main__':
    main()




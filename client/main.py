import os
from threading import Thread

from client import ChatClient


CLEARING_STRING = "\033[A                             \033[A"


def main():
    username = input('Enter user name: ')
    os.system('cls')
    client = ChatClient()
    client.connect('127.0.0.1', 7070)
    client.authorize(username)
    print(f'= <{client.username}> =======', end='\n\n')

    # Start processing incoming messages in a separate thread.
    server_echo_thread = Thread(target=client.echo_server)
    server_echo_thread.start()

    while True:
        message = input()
        print(CLEARING_STRING)
        client.send(message)


if __name__ == '__main__':
    main()


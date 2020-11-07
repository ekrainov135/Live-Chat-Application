import os
from threading import Thread

from client import ChatClient, CLEARING_STRING, ClientError


def console_input(prompt='', clearing=0):
    result = input(prompt)
    if clearing == 1:
        print(CLEARING_STRING)
    elif clearing == 2:
        os.system('cls' if os.name == 'nt' else 'clear')
    return result


def main():
    username = console_input('Enter user name: ', clearing=2)
    client = ChatClient()
    try:
        client.login(username, server=('127.0.0.1', 7070))
    except ClientError as e:
        print(f'Error: {e}')
        exit()

    print(f'= {client.username} =======\n\n')

    # Start processing incoming messages in a separate thread.
    server_echo_thread = Thread(target=client.echo_server)
    server_echo_thread.start()

    while True:
        try:
            message = console_input(clearing=1)
            client.send(message)
        except ClientError as e:
            print(f'Error: {e}')
            exit()
        except KeyboardInterrupt:
            client.logout()
            exit()


if __name__ == '__main__':
    main()


from core.server import ChatServerManager


def main():
    s = ChatServerManager()
    s.start('127.0.0.1', 7070)


if __name__ == '__main__':
    main()




from server import Server
from log import Log
from DataBaseHandler import Handler
import threading
import sys


def cmd():
    command = input()
    if command == 'exit':
        print('shutdown')
        sys.exit(0)


if __name__ == '__main__':
    log = Log('log.txt')
    with Handler('database.sqlite') as db_handler:
        HOST = '127.0.0.1'
        PORT = 1234
        server = Server(HOST, PORT, log, db_handler)
        server.start()

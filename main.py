from server import Server
from log import Log

if __name__ == '__main__':
    log = Log('log.txt')
    HOST = '127.0.0.1'
    PORT = 1234
    server = Server(HOST, PORT, log)
    server.start()

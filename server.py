import selectors
import socket
import HTTPHandler
from log import Log


class Server:
    def __init__(self, ip, port, log: Log, db_handler):
        self.addr = (ip, port)
        self.selector = selectors.DefaultSelector()
        # add attribute sock_list to store connected socks
        self.selector.sock_dict = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.addr)
        self.sock.listen()
        self.sock.setblocking(False)
        self.selector.register(self.sock, selectors.EVENT_READ)
        self.log = log
        self.db_handler = db_handler

    def start(self):
        self.log.log('server start')
        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                handler: HTTPHandler.Handler = key.data
                if handler:
                    handler.process(mask)
                else:
                    self.accept(key.fileobj)

    def accept(self, sock: socket.socket):
        conn, addr = sock.accept()
        conn.setblocking(False)
        self.log.log('accept connection to' + repr(addr))
        handler = HTTPHandler.Handler(self.selector, conn, addr, self.log, self.db_handler)
        self.selector.register(conn, selectors.EVENT_READ, data=handler)

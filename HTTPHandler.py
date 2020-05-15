import selectors
import socket

import lib


class Handler:
    target_list = ['register', 'login', 'friend-list', 'add-friend', 'sendmsg', 'offline']

    def __init__(self, sel, sock, addr, log):
        self.sel: selectors.BaseSelector = sel
        self.sock: socket.socket = sock
        self.addr = addr
        self.log = log
        self._recv_buffer = b''
        self._send_buffer = b''
        self.target = ''
        self._request_header = None
        self._body_len = 0
        self._request_body = b''
        self._response_created = False

    def process(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def _change_state(self, mode):
        if mode == 'w':
            self.log.log('request body: ' + repr(self._request_body))
            self.log.log(str(self.addr) + ' read complete')
            self.sel.modify(self.sock, selectors.EVENT_WRITE, data=self)
        elif mode == 'r':
            self.log.log(str(self.addr) + ' write complete')
            self.sel.modify(self.sock, selectors.EVENT_READ, data=self)

    def read(self):
        self._read()
        if not self._request_header:
            index = self._recv_buffer.find(b'\r\n\r\n')
            if index > 0:
                header = self._recv_buffer[:index]
                self._recv_buffer = self._recv_buffer[index:]
                start_line, self._request_header = lib.parse_header(header)
                if start_line[0] == 'POST':
                    self.target = start_line[1][1:]
                    self._body_len = int(self._request_header['Content-Length'])
                    self.log.log('request header: ' + repr(self._request_header))
                    self.log.log('request body len: ' + repr(self._body_len))
                    if self._body_len == 0:
                        self._change_state('w')
                else:
                    self.sock.send(b'')
        if self._request_header and len(self._recv_buffer) >= self._body_len:
            self._request_body = self._recv_buffer
            self.log.log('request body: ' + repr(self._request_body))
            self._change_state('w')

    def _read(self):
        data = self.sock.recv(1024)
        if data:
            self._recv_buffer += data

    def write(self):
        if not self._response_created:
            self.create_response(self.target, self._request_body)
        self._write()

    def create_response(self, target, body):
        obj = lib.parse_target(target, body)
        self._send_buffer = lib.get_message(obj)
        self._response_created = True

    def _write(self):
        if self._send_buffer:
            index = self.sock.send(self._send_buffer)
            self.log.log('send ' + repr(self._send_buffer[:index]) + ' to ' + str(self.addr))
            self._send_buffer = self._send_buffer[index:]
            if index and not self._send_buffer:
                self.close()
                self._change_state('r')

    def close(self):
        self.log.log('finish sending response to ' + str(self.addr))
        self._recv_buffer = b''
        self._send_buffer = b''
        self.target = ''
        self._request_header = None
        self._body_len = 0
        self._request_body = b''
        self._response_created = False

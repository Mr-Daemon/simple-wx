import json
import selectors
import socket
from threading import Thread

import DataBaseHandler
import lib


class Handler:
    def __init__(self, sel, sock, addr, log, db_handler):
        self.sel: selectors.BaseSelector = sel
        self.sock: socket.socket = sock
        self.addr = addr
        self.log = log
        self.db_handler: DataBaseHandler.Handler = db_handler
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
                    self.log.log('request target: ' + repr(self.target))
                    self.log.log('request header: ' + repr(self._request_header))
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
        if self._request_body and not self._response_created:
            self.create_response(self.target, self._request_body)
        self._write()

    def create_response(self, target, body):
        j_body = json.loads(body.decode('utf-8'))
        obj = self.db_handler.process_target(target, j_body, self.addr[0])
        self._send_buffer = lib.get_message(obj)
        self._response_created = True
        if target == 'send-msg':
            send_msg = {'from': j_body['username'], 'msg': j_body['msg']}
            ip = self.db_handler.get_ip(j_body['who'])
            self.log.log('send-msg: ' + repr(send_msg) + 'to ' + ip)
            Thread(target=lib.send_to_client, args=(ip, send_msg)).start()

    def _write(self):
        if self._send_buffer:
            index = self.sock.send(self._send_buffer)
            self.log.log('send ' + repr(self._send_buffer[:index]) + ' to ' + str(self.addr))
            self._send_buffer = self._send_buffer[index:]
            if index and not self._send_buffer:
                self.finish()
                self._change_state('r')

    def finish(self):
        self.log.log('finish sending response to ' + str(self.addr))
        self._recv_buffer = b''
        self._send_buffer = b''
        self.target = ''
        self._request_header = None
        self._body_len = 0
        self._request_body = b''
        self._response_created = False

    def close(self):
        self.sel.unregister(self.sock)
        self.sock.close()
        self.sock = None
        self.log.log('connection to ' + repr(self.addr) + ' closed')

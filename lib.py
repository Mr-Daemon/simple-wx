# require all bytes are encoded in utf-8
import json
import socket

ENCODING = 'utf-8'


def parse_header(header: bytes):
    array = list(filter(None, header.split(b'\r\n')))
    first_line = list(filter(None, array[0].decode(ENCODING).split(' ')))
    obj = dict()
    for entry in array[1:]:
        if entry:
            temp = entry.decode(ENCODING).split(':')
            obj[temp[0].strip()] = temp[1].strip()
    return first_line, obj


RESPONSE_HEADER = 'HTTP/1.1 200 OK\r\nContent-Type:text/json;charset=utf-8\r\nConnection:' \
                  'keep-alive\r\nContent-Length:{}\r\n\r\n'


def get_message(body):
    code = json.dumps(body).encode(ENCODING)
    result = RESPONSE_HEADER.format(len(code)).encode(ENCODING) + code
    return result


LISTEN_PORT = 1234

REQUEST_HEADER = 'POST / HTTP/1.1\r\nContent-Type:text/json;charset=utf-8\r\nConnection:' \
                 'keep-alive\r\nContent-Length:{}\r\n\r\n'


def send_to_client(host, body):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, LISTEN_PORT))
        b_body = json.dumps(body).encode(ENCODING)
        send_msg = REQUEST_HEADER.format(len(b_body)).encode(ENCODING) + b_body
        sock.sendall(send_msg)

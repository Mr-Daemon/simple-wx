# require all bytes are encoded in utf-8
import json

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


HEADER_TEMPLATE = 'HTTP/1.1 200 OK\r\nContent-Type:text/json;charset=utf-8\r\nConnection:' \
                  'keep-alive\r\nContent-Length:{}\r\n\r\n'


def get_message(body):
    code = json.dumps(body).encode(ENCODING)
    result = HEADER_TEMPLATE.format(len(code)).encode(ENCODING) + code
    return result

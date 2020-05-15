import sqlite3
import random


class Handler:
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cur = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('exit')
        self.connection.commit()
        self.connection.close()

    def process_target(self, target, body):
        if target == 'register':
            return self.register(body['username'], body['password'])
        elif target == 'login':
            return self.login(body['username'], body['password'])
        elif target == 'friends-list':
            return self.friends_list(body['username'], body['token'])
        elif target == 'add-friend':
            return self.add_friend(body)
        elif target == 'add-result':
            pass
        elif target == 'send-msg':
            return self.send_msg(body)
        elif target == 'offline':
            return self.offline(body['username'])

    def register(self, username, password):
        self.cur.execute('SELECT * FROM User WHERE username=?', (username,))
        row = self.cur.fetchone()
        result = dict()
        if row:
            result['code'] = 1
            result['msg'] = 'duplicate username'
        else:
            self.cur.execute('INSERT INTO User VALUES (?,?,?,?)',
                             (username, password, False, 0))
            self.connection.commit()
            result['code'] = 0
            result['msg'] = 'register successful'
        result['type'] = 'register'
        return result

    def login(self, username, password):
        self.cur.execute('SELECT * FROM User WHERE username=?', (username,))
        entry = self.cur.fetchone()
        print(repr(entry))
        result = dict()
        if not entry:
            result['code'] = 3
            result['msg'] = 'already login'
            result['type'] = 'login'
            result['token'] = 0
        elif entry[2]:
            result['code'] = 1
            result['msg'] = 'nonexist username'
            result['type'] = 'login'
            result['token'] = 0
        elif entry[1] == password:
            result['code'] = 0
            result['msg'] = 'login successful'
            result['type'] = 'login'
            token = random.randint(0x1, 0xFFFFFFFF)
            result['token'] = token
            self.cur.execute('''UPDATE User
                                SET isOnline = ?,
                                    token=?
                                WHERE username = ?;''', (True, token, username))
            self.connection.commit()
        else:
            result['code'] = 2
            result['msg'] = 'incorrect password'
            result['type'] = 'login'
            result['token'] = 0
        return result

    def friends_list(self, username, token):
        self.cur.execute('SELECT * FROM User WHERE username=?', (username,))
        entry = self.cur.fetchone()
        result = dict()
        if entry[3] == token:
            result['code'] = 0
            result['msg'] = 'get successful'
            result['type'] = 'friends-list'
            array = list()
            self.cur.execute('SELECT * FROM Friend WHERE name1=? OR name2=?', (username, username))
            entries = self.cur.fetchall()
            for entry in entries:
                if entry[0] == username:
                    array.append(entry[1])
                else:
                    array.append(entry[0])
            result['list'] = array
        else:
            result['code'] = 1
            result['msg'] = 'invalid token'
            result['type'] = 'friends-list'
            result['list'] = []
        return result

    def add_friend(self, obj):
        self.cur.execute('SELECT * FROM User WHERE username=?', (obj['username'],))
        entry = self.cur.fetchone()
        result = dict()
        if entry[3] == obj['token']:
            entry2 = self.cur.execute('SELECT * FROM User WHERE username=?', (obj['who'],)).fetchone()
            if obj['who'] in self.friends_list(obj['username'], obj['token'])['list']:
                result['code'] = 2
                result['msg'] = 'already friends'
            elif not entry2:
                result['code'] = 3
                result['msg'] = 'nonexist name'
            elif not entry2[2]:
                result['code'] = 4
                result['msg'] = 'user is offline'
            else:
                result['code'] = 0
                result['msg'] = 'send successful'
                # TODO send msg
        else:
            result['code'] = 1
            result['msg'] = 'invalid token'
        result['type'] = 'add-friend'
        return result

    def offline(self, username):
        self.cur.execute('SELECT * FROM User WHERE username=?', (username,))
        entry = self.cur.fetchone()
        if entry:
            self.cur.execute('''UPDATE User
                                SET isOnline = ?,
                                    token=?
                                WHERE username = ?;''', (False, 0, username))
            self.connection.commit()
        return {}

    def send_msg(self, obj):
        self.cur.execute('SELECT * FROM User WHERE username=?', (obj['username'],))
        entry = self.cur.fetchone()
        result = dict()
        if entry[3] == obj['token']:
            entry2 = self.cur.execute('SELECT * FROM User WHERE username=?', (obj['who'],)).fetchone()
            if entry2[2]:
                result['code'] = 0
                result['msg'] = 'send successful'
            else:
                result['code'] = 2
                result['msg'] = 'user is offline'
        else:
            result['code'] = 1
            result['msg'] = 'invalid token'
        result['type'] = 'send-msg'
        return result

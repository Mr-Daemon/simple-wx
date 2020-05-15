from datetime import datetime


class Log:
    def __init__(self, filename):
        self.filename=filename
        # self.f = open(filename, 'a')

    def log(self, msg):
        with open(self.filename,'a') as f:
            msg = '[' + datetime.now().strftime("%m-%d,%H:%M:%S") + ']: ' + msg
            print(msg)
            f.write(msg + '\n')

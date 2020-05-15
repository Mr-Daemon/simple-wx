import json
import random
import sqlite3
import lib

if __name__ == '__main__':
    test = {'a': '1', 'b': '2'}
    test.pop('a')
    print(test)

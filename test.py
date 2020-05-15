import json
import random
import sqlite3
import lib

if __name__ == '__main__':
    token = random.randint(0x1, 0xFFFFFFFF)
    print(token)

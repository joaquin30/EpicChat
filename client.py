#!/usr/bin/env python

import asyncio
import sys
import json
import datetime

import db_connection as db

from websockets.sync.client import connect

# def hello():
#     with connect(f'ws://localhost:8765/?user={sys.argv[1]}') as websocket:
#         websocket.send('Hello world!')
#         return 
#         message = websocket.recv()
#         print(f'Received: {message}')


def main():
    #todo
    #username = sys.argv[1]
    #interlocutor = sys.argv[2]
    #for easy local tests
    username =  'alina' #alina
    interlocutor = 'joaquin' #joaquin


    while True:
        commands = input('EpicChat > ').split()
        if len(commands) > 2:
            print('Command not recognized')
        elif len(commands) == 1 and (commands[0] == 'quit' or commands[0] == 'q'):
            break
        elif commands[0] == 'read' or commands[0] == 'r':
            db.read(username, interlocutor)
            print('Reading..')

        elif commands[0] == 'write' or commands[0] == 'w':
            #msg = input(f'To {commands[1]}: ')
            msg = input('Type message and press Enter:\n>')
            print(msg)

            write(msg, username,interlocutor )
        else:
            print('Command not recognized')

def write(msg, username, interlocutor):
    new_json = {
        'type': 'JM01',
        'from': username,
        'to': interlocutor,
        'timestamp': str(datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)),
        #todo local_id
        'local_id': 1,
        'content': msg
    }
    #todo add msg to database
    db.write(new_json)
    #print(json.dumps(new_json))





if __name__ == '__main__':
    main()

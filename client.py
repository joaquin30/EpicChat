#!/usr/bin/env python

import asyncio
import sys
from websockets.sync.client import connect

# def hello():
#     with connect(f"ws://localhost:8765/?user={sys.argv[1]}") as websocket:
#         websocket.send("Hello world!")
#         return 
#         message = websocket.recv()
#         print(f"Received: {message}")


def main():
    while True:
        commands = input('EpicChat> ').split()
        if len(commands) > 2:
            print('Command not recognized')
        elif len(commands) == 1 and (commands[0] == 'quit' or commands[0] == 'q'):
            break
        elif commands[0] == 'read' or commands[0] == 'r':
            #read()
            print("Reading..")
        elif commands[0] == 'write' or commands[0] == 'w':
            msg = input(f'To {commands[1]}: ')
            print(msg)
            #write(msg)
        else:
            print('Command not recognized')

if __name__ == '__main__':
    main()

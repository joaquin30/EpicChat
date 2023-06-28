#!/usr/bin/env python

import threading
import time
import sys
import json
from datetime import datetime
import db_connection as db
import websockets
import asyncio
import aioconsole

def makeMessage(msg, username, interlocutor):
    timestamp = str(datetime.utcnow())
    local_id = db.write(username, interlocutor, timestamp, msg)
    JM01_json = {
        'type': "JM01",
        'from': username,
        'to': interlocutor,
        'timestamp': timestamp,
        'local_id': str(local_id),
        'content': msg,
    }
    return json.dumps(JM01_json)

def showMessages(user1, user2):
    db.read(user1, user2)

def confirmation(conf_of, conf_id):
    json_msg = {
        'type': 'JM05',
        'confirmation_of': conf_of,
        'confirmation_id': conf_id
    }
    return json.dumps(json_msg)

async def processInput(websocket, username):
    while True:
        commands = (await aioconsole.ainput('EpicChat> ')).split()
        if len(commands) == 0:
            continue
        elif len(commands) == 1 and (commands[0] == 'quit' or commands[0] == 'q'):
            try:
                loop = asyncio.get_event_loop()
                for task in asyncio.all_tasks(loop):
                    task.cancel()
                # ~ loop.stop()
            except:
                break
        elif len(commands) == 1 and (commands[0] == 'help' or commands[0] == 'h'):
            print('''Commands:
    help: see this message
    quit: quit the program
    write <user>: send a message to <user>
    read <user>: show all the messages between you and <user>''')
        elif len(commands) == 2 and (commands[0] == 'read' or commands[0] == 'r'):
            showMessages(username, commands[1])
        elif len(commands) == 2 and (commands[0] == 'write' or commands[0] == 'w'):
            msg = await aioconsole.ainput('Type message: ')
            await websocket.send(makeMessage(msg, username, commands[1]))
        else:
            print('Command not recognized')


async def handleMessages(websocket):
    while True:
        # ~ print('xd')
        message = await websocket.recv()
        json_message = json.loads(message)
        # ~ print(message)
        if json_message['type'] == 'JM02': # new message
            db.write(json_message['from'], json_message['to'], json_message['timestamp'],
                json_message['content'], status='received')
            await websocket.send(confirmation('JM02', json_message['confirmation_id']))
        elif json_message['type'] == 'JM03': # change status to sent
            db.changeStatus(json_message['message_id'], 'sent')
            await websocket.send(confirmation('JM03', json_message['confirmation_id']))
        elif json_message['type'] == 'JM04': # change status to received
            db.changeStatus(json_message['message_id'], 'received')
            await websocket.send(confirmation('JM04', json_message['confirmation_id']))
            

async def main(username):
    async with websockets.connect(f'ws://localhost:8765/?user={username}') as websocket:
        try:
            asyncio.create_task(handleMessages(websocket))
            asyncio.create_task(processInput(websocket, username))
            await asyncio.Future() # run forever
        except:
            pass

if __name__ == '__main__':
    username = sys.argv[1]
    db.initDB(username)
    asyncio.run(main(username))

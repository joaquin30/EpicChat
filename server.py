import asyncio
from websockets.server import serve
from urllib import parse
import json
from datetime import datetime
import collections
import uuid

connections = {}
messages_to_send = {}
messages_sent = {}
messages_received = {}

async def handleMessages(websocket):
    # for obtaining username in "/?user=<username>"
    user = parse.parse_qs(parse.urlparse(websocket.path).query)['user'][0]
    connections[user] = websocket
    print('Connected:', user)

    if not user in messages_to_send:
        messages_to_send[user] = collections.deque()

    if not user in messages_sent:
        messages_sent[user] = collections.deque()

    if not user in messages_received:
        messages_received[user] = collections.deque()

    try:
        async for message in websocket:
            json_message = json.loads(message)
            print(json_message) # for logging
            if json_message['type'] == 'JM01': # Message
                messages_sent[user].append((json_message['local_id'], str(uuid.uuid4())))
                if not json_message['to'] in messages_to_send:
                    messages_to_send[json_message['to']] = collections.deque()
                messages_to_send[json_message['to']].append((json_message, str(uuid.uuid4())))
                
            elif json_message['type'] == 'JM05': # Confirmations
                if json_message['confirmation_of'] == 'JM02':
                    for i, v in enumerate(messages_to_send[user]):
                        if v[1] == json_message['confirmation_id']:
                            sender = v[0]['from']
                            local_id = v[0]['local_id']
                            del messages_to_send[user][i]
                            messages_received[sender].append((local_id, str(uuid.uuid4())))
                            break
                elif json_message['confirmation_of'] == 'JM03':
                    for i, v in enumerate(messages_sent[user]):
                        if v[1] == json_message['confirmation_id']:
                            del messages_to_send[user][i]
                            break
                elif json_message['confirmation_of'] == 'JM04':
                    for i, v in enumerate(messages_received[user]):
                        if v[1] == json_message['confirmation_id']:
                            del messages_to_send[user][i]
                            break
    finally:
        del connections[user]
        print('Disconnected:', user)
        

def changeStatus(msg_id, sent=False, received=False):
    json_msg = {
        'type': 'JM03',
        'message_id': msg_id,
    }
    if received:
        json_msg['type'] = 'JM04'
    return json.dumps(json_msg)


async def processQueues():
    while True:
        for user, websocket in connections.items():
            if len(messages_to_send[user]) > 0:
                message, conf_id = messages_to_send[user][0]
                try:
                    msg_for_receiver = json.loads(json.dumps(message)) # copy
                    del msg_for_receiver['local_id']
                    msg_for_receiver['confirmation_id'] = conf_id
                    msg_for_receiver['type'] = 'JM02'
                    print(json.dumps(msg_for_receiver))
                    await websocket.send(json.dumps(msg_for_receiver))
                    messages_to_send[user].append(messages_to_send[user].popleft())
                except:
                    continue
            if len(messages_sent[user]) > 0:
                message_id, conf_id = messages_sent[user][0]
                try:
                    print(changeStatus(message_id, sent=True))
                    await websocket.send(changeStatus(message_id, sent=True))
                    messages_sent[user].append(messages_sent[user].popleft())
                except:
                    continue
            if len(messages_received[user]) > 0:
                message_id, conf_id = messages_received[user][0]
                try:
                    print(changeStatus(message_id, received=True))
                    await websocket.send(changeStatus(message_id, received=True))
                    messages_received[user].append(messages_received[user].popleft())
                except:
                    continue
        await asyncio.sleep(.5) # For low CPU usage
                

async def main():
    async with serve(handleMessages, 'localhost', 8765):
        asyncio.create_task(processQueues())
        await asyncio.Future() # run forever


if __name__ == '__main__':
    asyncio.run(main())

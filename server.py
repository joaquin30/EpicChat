import asyncio
from websockets.server import serve
from urllib import parse
import json
from datetime import datetime

connections = {}
messages_to_send = {}
messages_sent = {}
messages_received = {}
confirmations = {}

async def handler(websocket):
    # for obtaining username in "/?user=<username>"
    user = parse.parse_qs(parse.urlparse(websocket.path).query)['user'][0]
    connections[user] = websocket

    if not user in messages_to_send:
        messages_to_send[user] = asyncio.PriorityQueue()

    if not user in messages_sent:
        messages_sent[user] = asyncio.PriorityQueue()

    if not user in messages_received:
        messages_received[user] = asyncio.PriorityQueue()

    try:
        async for message in websocket:
            json_message = json.loads(message)
            print(json_message) # for logging
            
            if json_message['type'] == 'JM01': # Message
                await messages_sent[user].put((json_message['timestamp'], json_message))
                await messages_to_send[user].put((json_message['timestamp'], json_message['local_id']))
            elif json_message['type'] == 'JM05': # Confirmations
                await confirmations[json_message['confirmation_of']].put(True)
    except:
        del connections[user]
        

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
            if not messages_to_send[user].empty():
                timestamp, message = await messages_to_send[user].get()
                try:
                    msg_for_receiver = message
                    del msg_for_receiver['local_id']
                    await websocket.send(json.dumps(msg_for_receiver))
                    await confirmations['JM02'].get()
                    await messages_received[user].put((datetime.now(), message['local_id']))
                except:
                    await messages_to_send[user].put((timestamp, message))

            if not messages_sent[user].empty():
                timestamp, message_id = await messages_sent[user].get()
                try:
                    await websocket.send(changeStatus(message_id, sent=True))
                    await confirmations['JM03'].get()
                except:
                    await messages_sent[user].put((timestamp, message_id))

            if not messages_received[user].empty():
                timestamp, message_id = await messages_received[user].get()
                try:
                    await websocket.send(changeStatus(message_id, received=True))
                    await confirmations['JM04'].get()
                except:
                    await messages_received[user].put((timestamp, message_id))
        
        await asyncio.sleep(0.1) # For low CPU usage
                

async def main():
    async with serve(handler, 'localhost', 8765):
        await asyncio.Future() # run forever

if __name__ == '__main__':
    for i in range(2, 5):
        confirmations[f'JM0{i}'] = asyncio.Queue()
        
    asyncio.run(processQueues())
    asyncio.run(main())

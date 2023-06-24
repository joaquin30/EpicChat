import asyncio
from websockets.server import serve
from urllib import parse
import json
from datetime import datetime

connections = {}
messages_to_send = {}
messages_sent = {}
messages_received = {}

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
            # for logging
            print(json_message)
            messages_sent[user].put((json_message['timestamp'], json_message))
            messages_to_send[user].put((json_message['timestamp'], json_message))
    except:
        del connections[user]
        

def changeStatus(msg_id, old, new):
    json_msg = {
        'type': 'JM03',
        'message_id': msg_id,   
        'old_status': old,
        'new_status': new
    }
    return json.dumps(json_msg)

async def update():
    while True:
        for user, websocket in connections.items():
            if not messages_to_send[user].empty():
                timestamp, message = messages_to_send[user].get()
                try:
                    msg_for_receiver = message
                    del msg_for_receiver['local_id']
                    await websocket.send(json.dumps(msg_for_receiver))
                    # TODO confirmation
                    messages_received.put((datetime.now(), message['local_id']))
                except:
                    messages_to_send[user].put((timestamp, msg))

            if not messages_sent[user].empty():
                timestamp, message_id = messages_sent[user].get()
                try:
                    await websocket.send(changeStatus(message_id, 0, 1))
                    # TODO confirmation
                except:
                    messages_sent[user].put((timestamp, message_id))

            if not messages_received[user].empty():
                timestamp, message_id = messages_received[user].get()
                try:
                    await websocket.send(changeStatus(message_id, 1, 2))
                    # TODO confirmation
                except:
                    messages_received[user].put((timestamp, message_id))
        
        # For low CPU usage
        await asyncio.sleep(0.1)
                

async def main():
    async with serve(handler, 'localhost', 8765):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(update())
    asyncio.run(main())

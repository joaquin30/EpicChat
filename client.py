#!/usr/bin/env python

import asyncio
import sys
from websockets.sync.client import connect

def hello():
    with connect(f"ws://localhost:8765/?user={sys.argv[1]}") as websocket:
        websocket.send("Hello world!")
        return 
        message = websocket.recv()
        print(f"Received: {message}")

hello()

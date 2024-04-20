#!/usr/bin/env python3
import asyncio
from datetime import datetime
import torchvision
from websockets.server import WebSocketServerProtocol, serve
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

async def handle(websocket: WebSocketServerProtocol):
    try:
        filename = f"{datetime.now()}.webm"
        with open(filename, "wb") as f:
            while True:
                message = await websocket.recv()
                assert isinstance(message, bytes), "Did not receive bytes"
                if not message:
                    break
                f.write(message)
        res = torchvision.io.read_file(filename)
        await websocket.send(f"Got tensor with shape {res.shape}")
    except ConnectionClosedOK:
        pass
    except ConnectionClosedError as e:
        print(e)

async def main():
    async with serve(handle, "localhost", 3001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from websockets.server import WebSocketServerProtocol, serve
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

async def handle(websocket: WebSocketServerProtocol):
    try:
        # Collect all of the data first
        all_data = bytearray()
        while True:
            message = await websocket.recv()
            assert isinstance(message, bytes), "Did not receive bytes"
            if not message:
                break
            all_data += message
        # TODO: pass this to the model and then stuff

    except ConnectionClosedOK:
        pass
    except ConnectionClosedError as e:
        print(e)

async def main():
    async with serve(handle, "localhost", 3000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

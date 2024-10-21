import asyncio
import websockets
import json
from datetime import datetime
from exchange_rate_fetcher import ExchangeRateFetcher

connected = set()


async def handler(websocket, path):
    connected.add(websocket)
    try:
        async for message in websocket:
            if message.startswith("exchange"):
                await handle_exchange_command(message, websocket)
            else:
                await broadcast(message)
    except websockets.ConnectionClosedOK:
        print("Connection closed gracefully.")
    finally:
        connected.remove(websocket)


async def handle_exchange_command(command, websocket):
    _, *args = command.split()
    if args:
        days = int(args[0])
        response = await ExchangeRateFetcher.get_exchange_rate(days)
        await websocket.send(json.dumps(response))
    else:
        await websocket.send(json.dumps({"error": "Usage: exchange <days>"}))


async def broadcast(message):
    if connected:
        await asyncio.wait([user.send(message) for user in connected])


async def start_server():
    async with websockets.serve(handler, "localhost", 6789):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(start_server())
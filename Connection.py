import os
import asyncio
import json
import time
import websockets
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_ID = os.getenv("BOT_ID")
DOMAIN = os.getenv("DOMAIN")

WS_URL = f"wss://{DOMAIN}/ws/device?id={BOT_ID}&token={TOKEN}"

PING_INTERVAL = 3.0  # seconds

async def handle_message(message: str): # Message Handling
    print("RAW:", message)

    try:
        body = json.loads(message)
    except json.JSONDecodeError:
        print("Invalid JSON")
        return

    msg_type = body.get("type")
    if not msg_type:
        print("Missing type field")
        return

    print("TYPE:", msg_type)

    if msg_type == "Action":
        print("ACTION:", body.get("action"))
        if "button" in body:
            print("BUTTON:", body["button"])


async def websocket_loop(): # WebSocket Loop
    last_ping = 0
    last_pong = time.time()

    while True:
        try:
            async with websockets.connect(
                WS_URL,
                ping_interval=None,  # manual ping (Arduino parity)
            ) as ws:

                print("WebSocket connected.")

                async def receiver():
                    nonlocal last_pong
                    async for msg in ws:
                        await handle_message(msg)

                recv_task = asyncio.create_task(receiver())

                while True:
                    now = time.time()

                    if now - last_pong > PING_INTERVAL and now - last_ping > 1:
                        last_ping = now
                        await ws.ping()

                    await asyncio.sleep(1 / 60)

        except Exception as e:
            print("WebSocket disconnected:", e)
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    print("Starting WebSocket test client...")
    asyncio.run(websocket_loop())
import asyncio
import importlib
import threading
import time
import requests
from flask import Flask
from pyrogram import idle
from Shashank.helper import join
from Shashank.modules import ALL_MODULES
from Shashank import app, clients, ids
from Shashank.modules.bot.start import restore_saved_sessions

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Flask app running on port 8000"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8000)

def keep_alive():
    while True:
        try:
            requests.get("https://userbot-r6zm.onrender.com", timeout=10)
        except Exception as e:
            print(f"Ping error: {e}")
        time.sleep(300)

async def start_all():
    await app.start()
    print("LOG: Waste X bot started.")

    for all_module in ALL_MODULES:
        try:
            importlib.import_module("Shashank.modules" + all_module)
            print(f"Successfully imported {all_module}")
        except Exception as e:
            print(f"Error importing {all_module}: {e}")

    for cli in clients:
        try:
            await cli.start()
            ex = await cli.get_me()
            await join(cli)
            print(f"Started {ex.first_name} 🔥")
            ids.append(ex.id)
        except Exception as e:
            print(f"Error starting client: {e}")

    await restore_saved_sessions()
    await idle()

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()
asyncio.get_event_loop().run_until_complete(start_all())

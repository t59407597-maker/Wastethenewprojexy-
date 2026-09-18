# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import os
import threading
import time
import requests
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Greeting(Resource):
    def get(self):
        return {"message": "Stranger Userbot is Up & Running!"}

api.add_resource(Greeting, '/')

def keep_alive():
    while True:
        try:
            url = "https://userbot-r6zm.onrender.com"
            print(f"Pinging {url}")
            requests.get(url)
        except Exception as e:
            print(f"Failed to ping: {e}")
        time.sleep(600) 

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

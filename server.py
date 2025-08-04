
import asyncio
import json
import os
from threading import Thread
from flask import Flask, request
from flask_socketio import SocketIO
import requests
from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = Flask(__name__)

io = SocketIO(app)

@io.event
def connect(auth):
    token = auth.get("token") if auth else None
    if token != VERIFY_TOKEN:
        return False  # desconecta

@io.event
def disconnect(sid):
    print(f"Cliente {sid} desconectado.")

@app.route("/", methods=["GET"])
def home():
    n_clients = len(io.server.manager.rooms.get('/', {}))
    return json.dumps({"n_clients": n_clients}), 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        print(f"Webhook chamado! mode={mode}, token={token}, challenge={challenge}")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        
        else:
            return "Erro de verificação", 403
        
    elif request.method == "POST":
        data = request.get_json()

        room = io.server.manager.rooms.get('/', {})
        if len(room) == 0:
            requests.post("https://verifai-w7pk.onrender.com/webhook", json=data)

        else:
            io.emit("webhook", data, broadcast=True)

        return "EVENT_RECEIVED", 200

async def loop():
    while True:
        await asyncio.sleep(10)
        try:
            requests.get("https://verifai-proxy-uxrm.onrender.com")
        except Exception as e:
            pass

def run_flask():
    io.run(app, "0.0.0.0", port=12345)
    
async def main():
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    try:
        await asyncio.create_task(loop())
    except asyncio.CancelledError:
        os._exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os._exit(0)

from flask import Flask, request
from flask_socketio import SocketIO
import os
import requests
from dotenv import load_dotenv
import asyncio
from threading import Thread

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = Flask(__name__)

io = SocketIO(app)

@io.event
def connect(sid):
    print(f"Cliente {sid} conectado.")

@io.event
def disconnect(sid):
    print(f"Cliente {sid} desconectado.")

@app.route("/", methods=["GET"])
def home():
    return "Ok"

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
        # data_args = request.args.to_dict()
        io.emit("webhook", data)
        return "EVENT_RECEIVED", 200

async def loop():
    while True:
        await asyncio.sleep(10)
        try:
            requests.get("https://verifai-proxy-uxrm.onrender.com")
        except Exception as e:
            pass

def run_flask():
    app.run("0.0.0.0", port=12345)
    
async def main():
    asyncio.create_task(loop())
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    try:
        await loop()
    except asyncio.CancelledError:
        os._exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os._exit(0)
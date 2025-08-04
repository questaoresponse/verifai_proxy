
import asyncio
import json
import os
from threading import Thread
from quart import Quart, request
import socketio
import requests
from dotenv import load_dotenv
import uvicorn

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

io = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = Quart(__name__)
asgi_app = socketio.ASGIApp(io, app)

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
    n_clients = sum(1 for _ in io.manager.get_participants('/', '/'))
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

        n_clients = sum(1 for _ in io.manager.get_participants('/', '/'))
        if n_clients == 0:
            requests.post("https://verifai-w7pk.onrender.com/webhook", json=data)

        else:
            io.emit("webhook", data)

        return "EVENT_RECEIVED", 200

async def keep_alive_loop():
    while True:
        await asyncio.sleep(10)
        try:
            requests.get("https://verifai-proxy-uxrm.onrender.com")
        except:
            pass

# Inicializa tudo no modo assíncrono
async def main():
    loop_task = asyncio.create_task(keep_alive_loop())
    config = uvicorn.Config(app=io.asgi_app, host="0.0.0.0", port=12345, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
    await loop_task

if __name__ == "__main__":
    import uvicorn
    loop = asyncio.get_event_loop()
    loop.create_task(keep_alive_loop())
    uvicorn.run(asgi_app, host="0.0.0.0", port=12345)
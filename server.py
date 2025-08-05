
import asyncio
import json
import os
from quart import Quart, request
import socketio
from dotenv import load_dotenv
import uvicorn
import httpx

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

io = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = Quart(__name__)
asgi_app = socketio.ASGIApp(io, app)

n_clients = 0

@io.event
def connect(_, __, auth):
    global n_clients
    n_clients += 1
    token = auth.get("token") if auth else None
    if token != VERIFY_TOKEN:
        return False  # desconecta

@io.event
def disconnect(sid):
    global n_clients
    n_clients -= 1
    print(f"Cliente {sid} desconectado.")

@app.route("/", methods=["GET"])
def home():
    return json.dumps({"n_clients": n_clients}), 200

@app.route("/webhook", methods=["GET", "POST"])
async def webhook():
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
        data = await request.get_json()

        if n_clients == 0:
            async with httpx.AsyncClient() as client:
                await client.post("https://verifai-w7pk.onrender.com/webhook", json=data)

        else:
            await io.emit("webhook", data)

        return "EVENT_RECEIVED", 200

async def keep_alive_loop():
    while True:
        await asyncio.sleep(10)
        try:
            async with httpx.AsyncClient() as client:
                await client.get("https://verifai-proxy-uxrm.onrender.com")
        except:
            pass

# Inicializa tudo no modo assíncrono
async def main():
    # Cria a tarefa do loop de keep-alive
    loop_task = asyncio.create_task(keep_alive_loop())

    # Configura e inicia o servidor Uvicorn
    config = uvicorn.Config(app=asgi_app, host="0.0.0.0", port=22222)
    server = uvicorn.Server(config)
    await server.serve()

    # (opcional) espera o loop de keep-alive (só após shutdown)
    await loop_task

# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os._exit(0)
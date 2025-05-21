from flask import Flask, request
import json
from flask_socketio import SocketIO
import os
import requests
import threading, time
from dotenv import load_dotenv

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
        rooms = io.server.manager.rooms.get('/', {})
        num_clients = sum(len(clients) for clients in rooms.values())
        if num_clients == 0:
            requests.post("https://verifai-8z3i.onrender.com", json=data)
        else:
            io.emit("webhook", data)
        # data_args = request.args.to_dict()
        return "EVENT_RECEIVED", 200
def send_requests():
    try:
        requests.get("https://verifai-proxy-uxrm.onrender.com")
    except Exception as e:
        print("error", e)
    threading.Timer(10, send_requests).start()  # executa a cada 2 segundos
    return None

send_requests()

if __name__ == "__main__":
    app.run("0.0.0.0", port=12345)
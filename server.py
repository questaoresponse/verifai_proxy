VERIFY_TOKEN = "meu_token_secreto"

from flask import Flask, request
import json
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()

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
    print("Endpoint raiz chamado!")
    return "Servidor rodando com pyngrok no Colab!"

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

if __name__ == "__main__":
    app.run("0.0.0.0", port=12345)
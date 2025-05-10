from flask import Flask
import socketio

# Cria uma instância do servidor Socket.IO
sio = socketio.Server(cors_allowed_origins='*')
app = Flask(__name__)

# Associa o Socket.IO com o Flask
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Evento de conexão
@sio.event
def connect(sid, environ):
    print(f"Cliente conectado: {sid}")
    sio.emit('message', {'data': 'Bem-vindo!'}, to=sid)

# Evento de mensagem personalizada
@sio.event
def my_event(sid, data):
    print(f"Recebido de {sid}: {data}")
    sio.emit('my_response', {'data': 'Recebido!'}, to=sid)

# Evento de desconexão
@sio.event
def disconnect(sid):
    print(f"Cliente desconectado: {sid}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)

# from google.colab import userdata
from flask import Flask, request
import google.generativeai as generai
import requests
import os
import socketio
sio = socketio.Client()
@sio.event
def connect():
    print("Conectado ao servidor")
    sio.emit('my_event', {'msg': 'Olá do cliente Python!'})


@app.route("/", methods=["GET"])
def home():
    print("Endpoint raiz chamado!")
    return "Servidor rodando com pyngrok no Colab!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    @sio.event
    def my_response(data):
        print("Resposta recebida:", data)
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
        print("Recebido POST do webhook:")
        try:
            messaging_event = data['entry'][0]['messaging'][0]
            sender_id = messaging_event['sender']['id']
            instagram_account_id = data['entry'][0]['id']
            text = messaging_event['message'].get('text')
            if text:
                print("Texto recebido na DM:", text)
                response = model.generate_content(text)
                print("Resposta do Gemini:", response.text)
                # Envia a resposta para o usuário no Instagram
                send_message_to_user(instagram_account_id, sender_id, response.text)
        except Exception as e:
            print("Não foi possível extrair o texto ou enviar resposta:", e)
        try:
            attachments = data['entry'][0]['messaging'][0]['message'].get('attachments', [])
            for att in attachments:
                if att['type'] == 'image':
                    image_url = att['payload'].get('url')
                    if image_url:
                        filename = get_next_image_filename()
                        img_data = requests.get(image_url).content
                        with open(filename, "wb") as handler:
                            handler.write(img_data)
                        print(f"Imagem salva como {filename}")
                    else:
                        print("Não foi possível obter a URL da imagem.")
        except Exception as e:
            print("Não foi possível salvar a imagem:", e)
        return "EVENT_RECEIVED", 200


import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---- Configurações (definidas no painel da Vercel: Environment Variables) ----
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
GRAPH_API_VERSION = os.environ.get("GRAPH_API_VERSION", "v20.0")

GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"


def send_text_message(to: str, body: str) -> dict:
    """Envia uma mensagem de texto simples usando a Cloud API do WhatsApp."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    response = requests.post(GRAPH_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


@app.route("/", methods=["GET"])
@app.route("/api/webhook", methods=["GET"])
def verify_webhook():
    """Endpoint de verificação exigido pela Meta ao configurar o webhook."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/", methods=["POST"])
@app.route("/api/webhook", methods=["POST"])
def receive_message():
    """Recebe eventos de mensagens enviadas pelo cliente e responde."""
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # Ignora eventos que não são mensagens (ex: status de entrega/leitura)
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        from_number = message["from"]
        msg_type = message.get("type")

        if msg_type == "text":
            text_body = message["text"]["body"]
            reply = build_reply(text_body)
            send_text_message(from_number, reply)
        else:
            send_text_message(
                from_number,
                "Por enquanto consigo responder apenas mensagens de texto. 🙂",
            )

    except (KeyError, IndexError, TypeError) as e:
        # Evento sem o formato esperado (ex: status de mensagem) - ignora
        print(f"Evento ignorado: {e}")

    # Sempre responder 200 rapidamente, senão a Meta reenvia o webhook
    return jsonify({"status": "received"}), 200


def build_reply(text: str) -> str:
    """Lógica simples de resposta automática baseada no texto recebido."""
    text_lower = text.strip().lower()

    if text_lower in ("oi", "ola", "olá", "menu"):
        return (
            "Olá! 👋 Como posso ajudar?\n\n"
            "1 - Falar com atendente\n"
            "2 - Horário de funcionamento\n"
            "3 - Endereço"
        )
    if text_lower == "1":
        return "Vou te transferir para um atendente humano em breve."
    if text_lower == "2":
        return "Atendemos de segunda a sexta, das 9h às 18h."
    if text_lower == "3":
        return "Estamos na Rua Exemplo, 123 - Rio de Janeiro."

    return f'Recebi sua mensagem: "{text}". Digite "menu" para ver as opções.'


# A Vercel chama a variável "app" do módulo como handler WSGI
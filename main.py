# main.py - Serveur webhook Flask pour bot WhatsApp

import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from bot import traiter_message

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# ─────────────────────────────────────────────
# WEBHOOK VERIFICATION (Meta l'appelle une fois)
# ─────────────────────────────────────────────

@app.route("/webhook", methods=["GET"])
def verifier_webhook():
    """Meta vérifie ton webhook lors de la configuration."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook vérifié avec succès !")
        return challenge, 200
    else:
        print("❌ Échec de vérification du webhook")
        return "Forbidden", 403


# ─────────────────────────────────────────────
# RÉCEPTION DES MESSAGES ENTRANTS
# ─────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def recevoir_message():
    """Reçoit les messages WhatsApp entrants."""
    data = request.get_json()

    try:
        entree = data["entry"][0]
        changements = entree["changes"][0]
        valeur = changements["value"]

        # Vérifier qu'il y a bien des messages
        if "messages" not in valeur:
            return jsonify({"status": "ok"}), 200

        message = valeur["messages"][0]
        telephone = message["from"]
        type_message = message["type"]

        # Traiter uniquement les messages texte
        if type_message == "text":
            texte = message["text"]["body"]
            print(f"📩 Message reçu de {telephone}: {texte}")
            traiter_message(telephone, texte)

        elif type_message == "audio":
            traiter_message(telephone, "[Message vocal reçu]")

        elif type_message == "image":
            traiter_message(telephone, "[Image reçue]")

        elif type_message == "document":
            traiter_message(telephone, "[Document reçu]")

        else:
            print(f"Type de message non géré : {type_message}")

    except (KeyError, IndexError) as e:
        print(f"Erreur parsing message: {e}")

    return jsonify({"status": "ok"}), 200


# ─────────────────────────────────────────────
# ROUTE DE TEST
# ─────────────────────────────────────────────

@app.route("/", methods=["GET"])
def accueil():
    return jsonify({
        "status": "running",
        "message": "DeslinBot WhatsApp est en ligne 🤖"
    }), 200


# ─────────────────────────────────────────────
# DÉMARRAGE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 DeslinBot démarré sur le port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

import os
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "ok", 200

# Puedes personalizar esta función para guardar archivos, nombres, duración, etc.
@bot.message_handler(func=lambda message: True, content_types=["text", "audio", "video", "voice", "document", "photo", "animation"])
def catch_all_messages(message):
    print(message)  # Solo visible en logs del servidor

    # Para que lo veas en Telegram también:
    detected_types = []
    if message.video:
        detected_types.append("video")
    if message.document:
        detected_types.append("document")
    if message.audio:
        detected_types.append("audio")
    if message.voice:
        detected_types.append("voice")
    if message.photo:
        detected_types.append("photo")
    if message.animation:
        detected_types.append("animation")

    if detected_types:
        bot.send_message(message.chat.id, f"Archivo detectado: {', '.join(detected_types)}")
    else:
        bot.send_message(message.chat.id, "Mensaje recibido, pero no se detectó archivo multimedia.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

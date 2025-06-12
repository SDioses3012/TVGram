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
@bot.message_handler(content_types=["audio", "video", "voice", "document"])
def handle_media(message):
    file_info = bot.get_file(message.audio.file_id if message.audio else message.video.file_id if message.video else message.voice.file_id if message.voice else message.document.file_id)
    file_name = message.audio.file_name if message.audio else message.document.file_name if message.document else "media"
    confirm_text = f"🎥 Archivo guardado: {file_name}"
    bot.send_message(message.chat.id, confirm_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

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
    file_id = None
    file_name = "media"

    if message.content_type == "audio":
        file_id = message.audio.file_id
        file_name = message.audio.file_name
    elif message.content_type == "video" and message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name
    elif message.content_type == "voice":
        file_id = message.voice.file_id
    elif message.content_type == "document":
        file_id = message.document.file_id
        file_name = message.document.file_name

    if file_id:
        file_info = bot.get_file(file_id)
        bot.send_message(message.chat.id, f"🎥 Archivo guardado: {file_name}")
    else:
        bot.send_message(message.chat.id, "⚠️ No se pudo procesar el archivo.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

import os
from flask import Flask, request, jsonify, send_from_directory
import telebot
from datetime import datetime

# Inicializar bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Inicializar Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'media'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Diccionario en memoria para almacenar la base de datos de medios
media_db = {}

@app.route("/")
def home():
    return "TVGram Server is running"

@app.route("/media", methods=["GET"])
def list_media():
    return jsonify(list(media_db.values()))

@app.route("/media/<file_id>", methods=["GET"])
def get_media_info(file_id):
    return jsonify(media_db.get(file_id, {}))

@app.route("/media/<file_id>/download", methods=["GET"])
def download_file(file_id):
    file_record = media_db.get(file_id)
    if not file_record:
        return "File not found", 404
    return send_from_directory(UPLOAD_FOLDER, file_record["filename"], as_attachment=True)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "ok", 200

@bot.message_handler(content_types=["audio", "video", "voice", "document"])
def handle_media(message):
    from datetime import datetime
    import traceback

    file_type = None
    file_name = "media"
    file_id = None

    if message.audio:
        file_type = "audio"
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio.mp3"
    elif message.video:
        file_type = "video"
        file_id = message.video.file_id
        file_name = message.video.file_name or "video.mp4"
    elif message.voice:
        file_type = "voice"
        file_id = message.voice.file_id
        file_name = f"voice_{file_id}.ogg"
    elif message.document:
        file_type = "document"
        file_id = message.document.file_id
        file_name = message.document.file_name or f"document_{file_id}"

    if file_id:
        try:
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            save_path = os.path.join("media", file_name)
            with open(save_path, "wb") as f:
                f.write(downloaded_file)

            media_db[file_id] = {
                "id": file_id,
                "filename": file_name,
                "type": file_type,
                "path": f"/media/{file_id}/download",
                "received_at": datetime.utcnow().isoformat() + "Z"
            }

            bot.send_message(message.chat.id, f"✅ Archivo guardado: {file_name}")

        except Exception as e:
            tb = traceback.format_exc()
            print(f"❌ Error al descargar el archivo:\n{tb}")
            bot.send_message(message.chat.id, f"❌ Error al descargar el archivo:\n{e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

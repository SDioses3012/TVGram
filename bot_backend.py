import os
import json
import sqlite3
from flask import Flask, request, jsonify
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# ─── Database Setup ─────────────────────────────
DB_FILE = "media_files.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT,
            file_name TEXT,
            media_type TEXT,
            duration INTEGER,
            origin TEXT,
            date TEXT
        )
        """)
        conn.commit()

init_db()

def save_media(file_id, file_name, media_type, duration, origin, date):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO media (file_id, file_name, media_type, duration, origin, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (file_id, file_name, media_type, duration, origin, date))
        conn.commit()

# ─── Bot Routes ─────────────────────────────────
@app.route("/")
def home():
    return "Bot running"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "ok", 200

@bot.message_handler(content_types=["video", "audio", "voice", "document"])
def handle_media(message):
    file = None
    file_name = "unknown"
    media_type = None
    duration = None

    if message.video:
        file = message.video
        file_name = file.file_name or f"video_{file.file_id}.mp4"
        media_type = "video"
        duration = file.duration
    elif message.audio:
        file = message.audio
        file_name = file.file_name or f"audio_{file.file_id}.mp3"
        media_type = "audio"
        duration = file.duration
    elif message.voice:
        file = message.voice
        file_name = f"voice_{file.file_id}.ogg"
        media_type = "voice"
        duration = file.duration
    elif message.document:
        file = message.document
        file_name = file.file_name or f"document_{file.file_id}"
        media_type = "document"

    origin = ""
    if message.forward_from_chat:
        origin = f"{message.forward_from_chat.title or message.forward_from_chat.username}"
    elif message.forward_from:
        origin = f"{message.forward_from.first_name or ''} {message.forward_from.last_name or ''}".strip()

    date = message.date

    if file:
        save_media(file.file_id, file_name, media_type, duration, origin, date)
        bot.send_message(message.chat.id, f"🎥 Archivo guardado: {file_name}")

# ─── API Endpoint for Client ────────────────────
@app.route("/media", methods=["GET"])
def get_media():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT file_id, file_name, media_type, duration, origin, date FROM media ORDER BY id DESC")
        rows = c.fetchall()
        media_list = []
        for r in rows:
            media_list.append({
                "file_id": r[0],
                "file_name": r[1],
                "media_type": r[2],
                "duration": r[3],
                "origin": r[4],
                "date": r[5],
                "url": f"https://api.telegram.org/file/bot{BOT_TOKEN}/{r[0]}"
            })
        return jsonify(media_list)

# ─── Run ────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# app.py
import os
import threading
import logging
from flask import Flask
import main  # твой основной файл с ботом

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/')
def index():
    return 'Sigma Media Bot is running!'

def run_bot():
    logging.info("Starting Telegram bot in background thread...")
    import asyncio
    asyncio.run(main.main())  # запускаем бота

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
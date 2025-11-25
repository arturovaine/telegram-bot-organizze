import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Configuration from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ALLOWED_CHAT_IDS = os.environ.get('ALLOWED_CHAT_IDS', '').split(',')


def send_telegram(chat_id, text):
    """Send message to Telegram"""
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    })


def is_authorized(chat_id):
    """Check if chat_id is authorized"""
    if not ALLOWED_CHAT_IDS or ALLOWED_CHAT_IDS == ['']:
        return False
    return str(chat_id) in ALLOWED_CHAT_IDS


@app.route('/', methods=['GET'])
def home():
    return 'Organizze Bot is running!'


@app.route('/', methods=['POST'])
def webhook():
    update = request.get_json()

    if not update or 'message' not in update:
        return 'OK'

    message = update['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')

    # Auth check
    if not is_authorized(chat_id):
        send_telegram(chat_id, f'⛔ Acesso não autorizado. Seu Chat ID: {chat_id}')
        return 'OK'

    # Handle /start and /help
    if text in ['/start', '/help']:
        help_msg = '''🤖 <b>Organizze Bot</b>

Bot em desenvolvimento...'''
        send_telegram(chat_id, help_msg)
        return 'OK'

    send_telegram(chat_id, 'Mensagem recebida!')
    return 'OK'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

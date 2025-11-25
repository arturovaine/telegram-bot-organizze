import os
import json
import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# Configuration from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ORGANIZZE_EMAIL = os.environ.get('ORGANIZZE_EMAIL')
ORGANIZZE_API_KEY = os.environ.get('ORGANIZZE_API_KEY')
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


def organizze_get(endpoint):
    """Make GET request to Organizze API"""
    url = f'https://api.organizze.com.br/rest/v2{endpoint}'
    response = requests.get(url, auth=(ORGANIZZE_EMAIL, ORGANIZZE_API_KEY), headers={
        'User-Agent': 'TelegramBot'
    })
    if response.status_code == 200:
        return response.json()
    return None


def get_financial_context():
    """Get financial data from Organizze"""
    today = datetime.now()
    start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    end_of_month = today.strftime('%Y-%m-%d')

    accounts = organizze_get('/accounts') or []
    transactions = organizze_get(f'/transactions?start_date={start_of_month}&end_date={end_of_month}') or []
    cards = organizze_get('/credit_cards') or []
    categories = organizze_get('/categories') or []

    # Calculate totals
    total_balance = 0
    accounts_list = []
    for acc in accounts:
        if not acc.get('archived'):
            balance = acc.get('default_balance', 0)
            total_balance += balance
            accounts_list.append({
                'name': acc['name'],
                'balance': balance
            })

    income = 0
    expenses = 0
    transactions_list = []

    # Category map
    category_map = {cat['id']: cat['name'] for cat in categories}

    for t in transactions:
        amount_cents = t.get('amount_cents', 0)
        if amount_cents > 0:
            income += amount_cents
        else:
            expenses += abs(amount_cents)

        transactions_list.append({
            'description': t.get('description'),
            'amount': amount_cents / 100,
            'date': t.get('date'),
            'category': category_map.get(t.get('category_id'), 'Sem categoria')
        })

    months_pt = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

    return {
        'today': today.strftime('%d/%m/%Y'),
        'month': months_pt[today.month - 1],
        'accounts': accounts_list,
        'totalBalance': total_balance,
        'income': income / 100,
        'expenses': expenses / 100,
        'balance': (income - expenses) / 100,
        'recentTransactions': transactions_list[-15:][::-1],
        'creditCards': [{'name': c['name'], 'limit': c['limit_cents'] / 100}
                        for c in cards if not c.get('archived')]
    }


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

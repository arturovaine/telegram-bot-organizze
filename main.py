import os
import io
import json
import requests
from flask import Flask, request
from datetime import datetime
import google.generativeai as genai
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# Configuration from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ORGANIZZE_EMAIL = os.environ.get('ORGANIZZE_EMAIL')
ORGANIZZE_API_KEY = os.environ.get('ORGANIZZE_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
ALLOWED_CHAT_IDS = os.environ.get('ALLOWED_CHAT_IDS', '').split(',')

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def send_telegram(chat_id, text):
    """Send message to Telegram"""
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    })


def send_photo(chat_id, photo_bytes, caption=''):
    """Send photo to Telegram"""
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
    files = {'photo': ('chart.png', photo_bytes, 'image/png')}
    data = {'chat_id': chat_id, 'caption': caption}
    requests.post(url, files=files, data=data)


def generate_pie_chart(transactions):
    """Generate pie chart of expenses by category"""
    category_totals = {}
    for t in transactions:
        if t['amount'] < 0:
            cat = t['category']
            category_totals[cat] = category_totals.get(cat, 0) + abs(t['amount'])

    if not category_totals:
        return None

    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_cats) > 8:
        top_cats = dict(sorted_cats[:7])
        others = sum(v for _, v in sorted_cats[7:])
        top_cats['Outros'] = others
    else:
        top_cats = dict(sorted_cats)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.Set3(range(len(top_cats)))

    wedges, texts, autotexts = ax.pie(
        top_cats.values(),
        labels=top_cats.keys(),
        autopct=lambda pct: f'R${pct/100*sum(top_cats.values()):.0f}\n({pct:.1f}%)',
        colors=colors,
        startangle=90
    )
    ax.set_title('Gastos por Categoria', fontsize=14, fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_bar_chart(transactions):
    """Generate bar chart of daily spending"""
    daily_totals = {}
    for t in transactions:
        date = t['date']
        if t['amount'] < 0:
            daily_totals[date] = daily_totals.get(date, 0) + abs(t['amount'])

    if not daily_totals:
        return None

    sorted_days = sorted(daily_totals.items())
    dates = [d[0][5:] for d in sorted_days]
    values = [d[1] for d in sorted_days]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(dates, values, color='#e74c3c', edgecolor='#c0392b')

    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Gastos (R$)', fontsize=12)
    ax.set_title('Gastos Diários', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'R${val:.0f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_summary_chart(financial_data):
    """Generate summary chart showing income vs expenses"""
    income = financial_data.get('income', 0)
    expenses = financial_data.get('expenses', 0)
    balance = financial_data.get('balance', 0)

    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ['Receitas', 'Despesas', 'Saldo']
    values = [income, expenses, balance]
    colors = ['#27ae60', '#e74c3c', '#3498db' if balance >= 0 else '#e74c3c']

    bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2)

    ax.set_ylabel('Valor (R$)', fontsize=12)
    ax.set_title(f'Resumo Financeiro - {financial_data.get("month", "").capitalize()}',
                 fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)

    for bar, val in zip(bars, values):
        ypos = bar.get_height() + (50 if val >= 0 else -150)
        ax.text(bar.get_x() + bar.get_width()/2, ypos,
                f'R${val:,.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


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


def ask_gemini(user_message, financial_data):
    """Ask Gemini AI about finances"""
    system_prompt = '''Você é um assistente financeiro pessoal. Responda em português de forma clara e concisa.
Use os dados financeiros fornecidos para responder perguntas sobre contas, saldos, transações e gastos.
Formate valores em Reais (R$). Seja direto e útil. Não use markdown, apenas texto simples com quebras de linha.

IMPORTANTE: Quando o usuário pedir gráficos, visualizações ou análises visuais, você DEVE incluir um comando especial no início da sua resposta:
- Para gráfico de pizza (gastos por categoria): comece com [CHART:PIE]
- Para gráfico de barras (gastos diários): comece com [CHART:BAR]
- Para gráfico de resumo (receitas x despesas x saldo): comece com [CHART:SUMMARY]

Exemplos de quando usar gráficos:
- "mostra um gráfico dos meus gastos" → [CHART:PIE]
- "gráfico de categorias" → [CHART:PIE]
- "gastos por dia" ou "gráfico diário" → [CHART:BAR]
- "resumo visual" ou "gráfico de receitas e despesas" → [CHART:SUMMARY]

Se o usuário não pedir gráfico especificamente, responda apenas com texto.'''

    context = f"Dados financeiros atuais:\n{json.dumps(financial_data, indent=2, ensure_ascii=False)}"

    prompt = f"{system_prompt}\n\n{context}\n\nPergunta do usuário: {user_message}"

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Desculpe, não consegui processar sua pergunta. Tente novamente."


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
        help_msg = '''🤖 <b>Organizze Bot com IA</b>

Pergunte qualquer coisa sobre suas finanças!

Exemplos:
• Qual meu saldo total?
• Quanto gastei esse mês?
• Quais foram minhas últimas transações?
• Resumo das minhas finanças
• Quanto tenho na conta Itaú?'''
        send_telegram(chat_id, help_msg)
        return 'OK'

    # Get financial data and ask Gemini
    financial_data = get_financial_context()
    response = ask_gemini(text, financial_data)

    # Check for chart commands
    chart_sent = False
    if '[CHART:PIE]' in response:
        chart_data = generate_pie_chart(financial_data.get('recentTransactions', []))
        if chart_data:
            caption = response.replace('[CHART:PIE]', '').strip()[:1024]
            send_photo(chat_id, chart_data, caption)
            chart_sent = True
    elif '[CHART:BAR]' in response:
        chart_data = generate_bar_chart(financial_data.get('recentTransactions', []))
        if chart_data:
            caption = response.replace('[CHART:BAR]', '').strip()[:1024]
            send_photo(chat_id, chart_data, caption)
            chart_sent = True
    elif '[CHART:SUMMARY]' in response:
        chart_data = generate_summary_chart(financial_data)
        if chart_data:
            caption = response.replace('[CHART:SUMMARY]', '').strip()[:1024]
            send_photo(chat_id, chart_data, caption)
            chart_sent = True

    if not chart_sent:
        send_telegram(chat_id, response)

    return 'OK'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

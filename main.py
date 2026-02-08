"""
Organizze Telegram Bot - Main application
Refactored modular architecture
"""

import os
from flask import Flask, request
from datetime import datetime
import logging

# Local imports
from organizze_client import OrganizzeClient, OrganizzeAPIError
from ai_assistant import GeminiAssistant
from telegram_bot import TelegramBot, AuthManager, get_help_message, QUICK_COMMANDS
from charts import (
    generate_pie_chart,
    generate_bar_chart,
    generate_summary_chart,
    generate_budget_progress_chart,
    generate_invoice_history_chart
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize services
organizze = OrganizzeClient()
ai = GeminiAssistant()
telegram = TelegramBot()
auth = AuthManager()


def get_financial_context() -> dict:
    """
    Get comprehensive financial data from Organizze

    Returns:
        Dict with financial data for AI context
    """
    today = datetime.now()
    start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    end_of_month = today.strftime('%Y-%m-%d')

    try:
        # Fetch all data
        accounts = organizze.get_accounts()
        transactions = organizze.get_transactions(start_of_month, end_of_month)
        cards = organizze.get_credit_cards()
        categories = organizze.get_categories()
        budgets = organizze.get_budgets(today.year, today.month)

        # Build category map
        category_map = {cat['id']: cat['name'] for cat in categories}

        # Calculate account totals
        total_balance = 0
        accounts_list = []
        for acc in accounts:
            if not acc.get('archived'):
                balance = acc.get('default_balance', 0)
                total_balance += balance
                accounts_list.append({
                    'id': acc['id'],
                    'name': acc['name'],
                    'type': acc.get('type', 'checking'),
                    'balance': balance
                })

        # Process transactions
        income = 0
        expenses = 0
        transactions_list = []

        for t in transactions:
            amount_cents = t.get('amount_cents', 0)
            if amount_cents > 0:
                income += amount_cents
            else:
                expenses += abs(amount_cents)

            transactions_list.append({
                'id': t.get('id'),
                'description': t.get('description'),
                'amount': amount_cents / 100,
                'date': t.get('date'),
                'category': category_map.get(t.get('category_id'), 'Sem categoria'),
                'category_id': t.get('category_id'),
                'tags': t.get('tags', []),
                'notes': t.get('notes'),
                'paid': t.get('paid', True)
            })

        # Process credit cards
        credit_cards_list = []
        for card in cards:
            if not card.get('archived'):
                credit_cards_list.append({
                    'id': card['id'],
                    'name': card['name'],
                    'network': card.get('network', ''),
                    'limit': card.get('limit_cents', 0) / 100,
                    'closing_day': card.get('closing_day'),
                    'due_day': card.get('due_day')
                })

        # Process budgets
        budgets_list = []
        for budget in budgets:
            budgets_list.append({
                'category_id': budget.get('category_id'),
                'category': category_map.get(budget.get('category_id'), 'Desconhecida'),
                'amount': budget.get('amount_cents', 0) / 100,
                'predicted': budget.get('predicted', 0),
                'actual': budget.get('actual', 0)
            })

        # Month names in Portuguese
        months_pt = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                     'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

        return {
            'today': today.strftime('%d/%m/%Y'),
            'month': months_pt[today.month - 1],
            'year': today.year,
            'accounts': accounts_list,
            'totalBalance': total_balance,
            'income': income / 100,
            'expenses': expenses / 100,
            'balance': (income - expenses) / 100,
            'recentTransactions': transactions_list[-15:][::-1],
            'allTransactions': transactions_list,
            'creditCards': credit_cards_list,
            'budgets': budgets_list,
            'categories': list(category_map.values())
        }

    except OrganizzeAPIError as e:
        logger.error(f"Failed to fetch financial data: {e}")
        return {
            'error': str(e),
            'today': datetime.now().strftime('%d/%m/%Y'),
            'month': 'unknown'
        }


def handle_chart_request(chat_id: int, chart_type: str, financial_data: dict, response_text: str):
    """
    Handle chart generation and sending

    Args:
        chat_id: Telegram chat ID
        chart_type: Type of chart (PIE, BAR, SUMMARY, BUDGET, INVOICE)
        financial_data: Financial data for chart
        response_text: AI response text to use as caption
    """
    chart_data = None
    caption = ai.remove_command_tags(response_text).strip()[:1024]

    if chart_type == 'PIE':
        chart_data = generate_pie_chart(financial_data.get('recentTransactions', []))
    elif chart_type == 'BAR':
        chart_data = generate_bar_chart(financial_data.get('recentTransactions', []))
    elif chart_type == 'SUMMARY':
        chart_data = generate_summary_chart(financial_data)
    elif chart_type == 'BUDGET':
        budgets = financial_data.get('budgets', [])
        category_map = {b['category_id']: b['category'] for b in budgets}
        chart_data = generate_budget_progress_chart(budgets, category_map)

    if chart_data:
        telegram.send_photo(chat_id, chart_data, caption)
        return True
    else:
        telegram.send_message(chat_id, "Desculpe, não consegui gerar o gráfico. Dados insuficientes.")
        return False


@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return 'Organizze Bot is running!'


@app.route('/', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    update = request.get_json()

    if not update or 'message' not in update:
        return 'OK'

    message = update['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')

    # Authorization check
    if not auth.is_authorized(chat_id):
        telegram.send_message(
            chat_id,
            f'⛔ Acesso não autorizado. Seu Chat ID: {chat_id}\n\n'
            'Entre em contato com o administrador para liberar acesso.'
        )
        logger.warning(f"Unauthorized access attempt from chat_id: {chat_id}")
        return 'OK'

    # Handle /start and /help
    if text in ['/start', '/help']:
        telegram.send_message(chat_id, get_help_message())
        return 'OK'

    # Handle quick commands
    if text in QUICK_COMMANDS:
        text = QUICK_COMMANDS[text]

    # Show typing indicator
    telegram.send_chat_action(chat_id, 'typing')

    try:
        # Get financial context
        financial_data = get_financial_context()

        if 'error' in financial_data:
            telegram.send_message(
                chat_id,
                f"❌ Erro ao buscar dados financeiros: {financial_data['error']}"
            )
            return 'OK'

        # Ask AI
        response = ai.ask(text, financial_data)

        # Check for chart command
        chart_type = ai.extract_chart_command(response)
        if chart_type:
            handle_chart_request(chat_id, chart_type, financial_data, response)
        else:
            # Send text response
            clean_response = ai.remove_command_tags(response)
            telegram.send_message(chat_id, clean_response)

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        telegram.send_message(
            chat_id,
            "❌ Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
        )

    return 'OK'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

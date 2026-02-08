"""
Telegram Bot handlers and utilities
"""

import os
import requests
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram Bot API wrapper"""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize Telegram bot

        Args:
            token: Telegram bot token (defaults to TELEGRAM_TOKEN env var)
        """
        self.token = token or os.environ.get('TELEGRAM_TOKEN')
        if not self.token:
            raise ValueError("Telegram token is required")

        self.base_url = f'https://api.telegram.org/bot{self.token}'

    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = 'HTML',
        disable_web_page_preview: bool = False
    ) -> bool:
        """
        Send text message to chat

        Args:
            chat_id: Telegram chat ID
            text: Message text (max 4096 characters)
            parse_mode: Parse mode (HTML, Markdown, MarkdownV2)
            disable_web_page_preview: Disable link previews

        Returns:
            True if successful, False otherwise
        """
        url = f'{self.base_url}/sendMessage'

        # Split long messages
        if len(text) > 4096:
            chunks = self._split_message(text, 4096)
            for chunk in chunks:
                self.send_message(chat_id, chunk, parse_mode, disable_web_page_preview)
            return True

        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def send_photo(
        self,
        chat_id: int,
        photo_bytes: bytes,
        caption: str = '',
        parse_mode: str = 'HTML'
    ) -> bool:
        """
        Send photo to chat

        Args:
            chat_id: Telegram chat ID
            photo_bytes: Photo image bytes (PNG, JPG)
            caption: Photo caption (max 1024 characters)
            parse_mode: Parse mode for caption

        Returns:
            True if successful, False otherwise
        """
        url = f'{self.base_url}/sendPhoto'

        # Truncate caption if too long
        if len(caption) > 1024:
            caption = caption[:1021] + '...'

        files = {'photo': ('chart.png', photo_bytes, 'image/png')}
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': parse_mode
        }

        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            return False

    def send_chat_action(self, chat_id: int, action: str = 'typing') -> bool:
        """
        Send chat action (typing, upload_photo, etc.)

        Args:
            chat_id: Telegram chat ID
            action: Action type

        Returns:
            True if successful
        """
        url = f'{self.base_url}/sendChatAction'
        payload = {'chat_id': chat_id, 'action': action}

        try:
            requests.post(url, json=payload, timeout=5)
            return True
        except Exception as e:
            logger.error(f"Failed to send chat action: {e}")
            return False

    def _split_message(self, text: str, max_length: int = 4096) -> List[str]:
        """Split long message into chunks"""
        chunks = []
        while len(text) > max_length:
            # Try to split at newline
            split_pos = text.rfind('\n', 0, max_length)
            if split_pos == -1:
                split_pos = max_length
            chunks.append(text[:split_pos])
            text = text[split_pos:].lstrip()
        if text:
            chunks.append(text)
        return chunks


class AuthManager:
    """Manages authorization for bot access"""

    def __init__(self, allowed_chat_ids: Optional[List[str]] = None):
        """
        Initialize authorization manager

        Args:
            allowed_chat_ids: List of allowed chat IDs (defaults to ALLOWED_CHAT_IDS env var)
        """
        if allowed_chat_ids is None:
            ids_str = os.environ.get('ALLOWED_CHAT_IDS', '')
            allowed_chat_ids = ids_str.split(',') if ids_str else []

        self.allowed_chat_ids = [str(id_).strip() for id_ in allowed_chat_ids if id_.strip()]

    def is_authorized(self, chat_id: int) -> bool:
        """
        Check if chat ID is authorized

        Args:
            chat_id: Telegram chat ID to check

        Returns:
            True if authorized, False otherwise
        """
        if not self.allowed_chat_ids:
            logger.warning("No allowed chat IDs configured - denying access")
            return False

        return str(chat_id) in self.allowed_chat_ids

    def add_chat_id(self, chat_id: int) -> None:
        """Add chat ID to allowed list"""
        chat_id_str = str(chat_id)
        if chat_id_str not in self.allowed_chat_ids:
            self.allowed_chat_ids.append(chat_id_str)
            logger.info(f"Added chat ID {chat_id} to allowed list")

    def remove_chat_id(self, chat_id: int) -> None:
        """Remove chat ID from allowed list"""
        chat_id_str = str(chat_id)
        if chat_id_str in self.allowed_chat_ids:
            self.allowed_chat_ids.remove(chat_id_str)
            logger.info(f"Removed chat ID {chat_id} from allowed list")


def get_help_message() -> str:
    """Get bot help message"""
    return '''🤖 <b>Organizze Bot com IA</b>

Pergunte qualquer coisa sobre suas finanças ou use os comandos rápidos:

📊 <b>Gráficos</b>
/gastos_categoria - Gráfico de pizza por categoria
/gastos_diarios - Gráfico de barras diário
/resumo_visual - Resumo receitas x despesas

💰 <b>Consultas</b>
/saldo - Saldo total das contas
/extrato - Últimas transações
/resumo - Resumo financeiro do mês

💳 <b>Cartões de Crédito</b>
/cartoes - Info dos cartões de crédito
/fatura - Fatura atual do cartão
/faturas - Histórico de faturas

📈 <b>Orçamento</b>
/orcamento - Ver progresso do orçamento mensal
/metas - Metas por categoria

🔄 <b>Gestão</b>
/gasto - Registrar novo gasto
/receita - Registrar nova receita
/transferir - Transferir entre contas

❓ <b>Ou pergunte naturalmente:</b>
"Quanto gastei com alimentação?"
"Qual meu saldo no Nubank?"
"Mostre um gráfico dos meus gastos"
"Registre um gasto de 50 reais com almoço"'''


QUICK_COMMANDS = {
    # Charts
    '/gastos_categoria': 'Mostre um gráfico de pizza dos meus gastos por categoria',
    '/gastos_diarios': 'Mostre um gráfico de barras dos meus gastos diários',
    '/resumo_visual': 'Mostre um gráfico de resumo com receitas, despesas e saldo',

    # Queries
    '/saldo': 'Qual é o saldo total de todas as minhas contas?',
    '/extrato': 'Mostre minhas últimas transações',
    '/resumo': 'Faça um resumo das minhas finanças deste mês',

    # Credit cards
    '/cartoes': 'Quais são meus cartões de crédito e seus limites?',
    '/fatura': 'Mostre a fatura atual do meu cartão de crédito',
    '/faturas': 'Mostre o histórico de faturas do cartão',

    # Budget
    '/orcamento': 'Mostre o progresso do meu orçamento mensal',
    '/metas': 'Quais são minhas metas de gastos por categoria?',
}

"""
AI Assistant using Google Gemini for financial queries
"""

import os
import json
from typing import Dict, Optional
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)


class GeminiAssistant:
    """AI assistant for financial queries using Gemini"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = 'gemini-2.0-flash'):
        """
        Initialize Gemini AI assistant

        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
            model_name: Gemini model to use
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def ask(self, user_message: str, financial_data: Dict) -> str:
        """
        Ask Gemini AI about finances

        Args:
            user_message: User's question
            financial_data: Financial context data

        Returns:
            AI response text with optional chart commands
        """
        system_prompt = self._build_system_prompt()
        context = self._format_financial_context(financial_data)
        full_prompt = f"{system_prompt}\n\n{context}\n\nPergunta do usuário: {user_message}"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "Desculpe, não consegui processar sua pergunta. Tente novamente."

    def _build_system_prompt(self) -> str:
        """Build system prompt for Gemini"""
        return '''Você é um assistente financeiro pessoal. Responda em português de forma clara e concisa.
Use os dados financeiros fornecidos para responder perguntas sobre contas, saldos, transações e gastos.
Formate valores em Reais (R$). Seja direto e útil. Não use markdown, apenas texto simples com quebras de linha.

IMPORTANTE: Quando o usuário pedir gráficos, visualizações ou análises visuais, você DEVE incluir um comando especial no início da sua resposta:
- Para gráfico de pizza (gastos por categoria): comece com [CHART:PIE]
- Para gráfico de barras (gastos diários): comece com [CHART:BAR]
- Para gráfico de resumo (receitas x despesas x saldo): comece com [CHART:SUMMARY]
- Para gráfico de progresso do orçamento: comece com [CHART:BUDGET]
- Para gráfico de histórico de faturas: comece com [CHART:INVOICE]
- Para gráfico de comparação mensal: comece com [CHART:COMPARISON]

Exemplos de quando usar gráficos:
- "mostra um gráfico dos meus gastos" → [CHART:PIE]
- "gráfico de categorias" → [CHART:PIE]
- "gastos por dia" ou "gráfico diário" → [CHART:BAR]
- "resumo visual" ou "gráfico de receitas e despesas" → [CHART:SUMMARY]
- "progresso do orçamento" → [CHART:BUDGET]
- "histórico de faturas" → [CHART:INVOICE]
- "comparar com mês passado" → [CHART:COMPARISON]

Se o usuário não pedir gráfico especificamente, responda apenas com texto.

CAPACIDADES DE AÇÃO:
Você também pode sugerir ações quando apropriado. Use comandos especiais:
- [ACTION:CREATE_EXPENSE] - Quando usuário quer registrar gasto
- [ACTION:CREATE_INCOME] - Quando usuário quer registrar receita
- [ACTION:CREATE_TRANSFER] - Quando usuário quer transferir entre contas
- [ACTION:CREATE_CATEGORY] - Quando usuário quer criar categoria
- [ACTION:SET_BUDGET] - Quando usuário quer definir meta de orçamento

Exemplo:
Usuário: "registrar gasto de 50 reais com almoço"
Você: "[ACTION:CREATE_EXPENSE] Vou registrar um gasto de R$ 50,00 com almoço. Qual categoria deseja usar?"'''

    def _format_financial_context(self, financial_data: Dict) -> str:
        """Format financial data as context for AI"""
        return f"Dados financeiros atuais:\n{json.dumps(financial_data, indent=2, ensure_ascii=False)}"

    def extract_chart_command(self, response: str) -> Optional[str]:
        """
        Extract chart command from AI response

        Args:
            response: AI response text

        Returns:
            Chart command (PIE, BAR, SUMMARY, etc.) or None
        """
        chart_commands = ['PIE', 'BAR', 'SUMMARY', 'BUDGET', 'INVOICE', 'COMPARISON']
        for cmd in chart_commands:
            if f'[CHART:{cmd}]' in response:
                return cmd
        return None

    def extract_action_command(self, response: str) -> Optional[str]:
        """
        Extract action command from AI response

        Args:
            response: AI response text

        Returns:
            Action command (CREATE_EXPENSE, CREATE_INCOME, etc.) or None
        """
        action_commands = [
            'CREATE_EXPENSE',
            'CREATE_INCOME',
            'CREATE_TRANSFER',
            'CREATE_CATEGORY',
            'SET_BUDGET'
        ]
        for cmd in action_commands:
            if f'[ACTION:{cmd}]' in response:
                return cmd
        return None

    def remove_command_tags(self, response: str) -> str:
        """Remove all command tags from response text"""
        import re
        # Remove [CHART:*] tags
        response = re.sub(r'\[CHART:\w+\]', '', response)
        # Remove [ACTION:*] tags
        response = re.sub(r'\[ACTION:\w+\]', '', response)
        return response.strip()

"""
Chart generation for financial data visualization
"""

import io
from typing import Optional, List, Dict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def generate_pie_chart(transactions: List[Dict]) -> Optional[bytes]:
    """
    Generate pie chart of expenses by category

    Args:
        transactions: List of transaction dicts with 'amount' and 'category' keys

    Returns:
        PNG image bytes or None if no data
    """
    category_totals = {}
    for t in transactions:
        if t['amount'] < 0:
            cat = t['category']
            category_totals[cat] = category_totals.get(cat, 0) + abs(t['amount'])

    if not category_totals:
        return None

    # Sort and limit to top 8 categories
    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_cats) > 8:
        top_cats = dict(sorted_cats[:7])
        others = sum(v for _, v in sorted_cats[7:])
        top_cats['Outros'] = others
    else:
        top_cats = dict(sorted_cats)

    # Create pie chart
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

    # Convert to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_bar_chart(transactions: List[Dict]) -> Optional[bytes]:
    """
    Generate bar chart of daily spending

    Args:
        transactions: List of transaction dicts with 'amount' and 'date' keys

    Returns:
        PNG image bytes or None if no data
    """
    daily_totals = {}
    for t in transactions:
        date = t['date']
        if t['amount'] < 0:
            daily_totals[date] = daily_totals.get(date, 0) + abs(t['amount'])

    if not daily_totals:
        return None

    # Sort by date
    sorted_days = sorted(daily_totals.items())
    dates = [d[0][5:] for d in sorted_days]  # Remove year prefix
    values = [d[1] for d in sorted_days]

    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(dates, values, color='#e74c3c', edgecolor='#c0392b')

    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Gastos (R$)', fontsize=12)
    ax.set_title('Gastos Diários', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'R${val:.0f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_summary_chart(financial_data: Dict) -> Optional[bytes]:
    """
    Generate summary chart showing income vs expenses vs balance

    Args:
        financial_data: Dict with 'income', 'expenses', 'balance', 'month' keys

    Returns:
        PNG image bytes or None if no data
    """
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

    # Add value labels
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


def generate_budget_progress_chart(budgets: List[Dict], categories: Dict[int, str]) -> Optional[bytes]:
    """
    Generate horizontal bar chart showing budget progress by category

    Args:
        budgets: List of budget dicts with category_id, amount, actual
        categories: Dict mapping category_id to category name

    Returns:
        PNG image bytes or None if no data
    """
    if not budgets:
        return None

    # Prepare data
    category_names = []
    budget_amounts = []
    actual_amounts = []
    progress_percentages = []

    for budget in budgets[:10]:  # Limit to top 10
        cat_name = categories.get(budget['category_id'], f"Cat {budget['category_id']}")
        category_names.append(cat_name)
        budget_amounts.append(budget['amount'])
        actual_amounts.append(budget.get('actual', 0))
        progress = (budget.get('actual', 0) / budget['amount'] * 100) if budget['amount'] > 0 else 0
        progress_percentages.append(progress)

    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    y_pos = range(len(category_names))

    # Plot budget as background (lighter)
    ax.barh(y_pos, budget_amounts, color='#ecf0f1', label='Orçamento')

    # Plot actual spending on top
    colors = ['#27ae60' if p <= 100 else '#e74c3c' for p in progress_percentages]
    ax.barh(y_pos, actual_amounts, color=colors, label='Gasto Real')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(category_names)
    ax.set_xlabel('Valor (R$)', fontsize=12)
    ax.set_title('Progresso do Orçamento por Categoria', fontsize=14, fontweight='bold')
    ax.legend()

    # Add percentage labels
    for i, (actual, budget, pct) in enumerate(zip(actual_amounts, budget_amounts, progress_percentages)):
        label = f'{pct:.0f}%'
        ax.text(max(actual, budget) + 10, i, label, va='center', fontsize=9)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_invoice_history_chart(invoices: List[Dict]) -> Optional[bytes]:
    """
    Generate line chart of invoice amounts over time

    Args:
        invoices: List of invoice dicts with 'date' and 'amount_cents' keys

    Returns:
        PNG image bytes or None if no data
    """
    if not invoices:
        return None

    # Sort by date
    sorted_invoices = sorted(invoices, key=lambda x: x['date'])
    dates = [inv['date'][5:7] + '/' + inv['date'][:4] for inv in sorted_invoices]  # MM/YYYY
    amounts = [inv.get('amount_cents', 0) / 100 for inv in sorted_invoices]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, amounts, marker='o', linewidth=2, color='#3498db')
    ax.fill_between(range(len(dates)), amounts, alpha=0.3, color='#3498db')

    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel('Valor da Fatura (R$)', fontsize=12)
    ax.set_title('Histórico de Faturas do Cartão', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')

    # Add value labels
    for i, (date, amount) in enumerate(zip(dates, amounts)):
        ax.text(i, amount + max(amounts) * 0.02, f'R${amount:.2f}',
                ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_month_comparison_chart(
    current_month: Dict,
    previous_month: Dict
) -> Optional[bytes]:
    """
    Generate comparison chart between two months

    Args:
        current_month: Dict with 'income', 'expenses', 'balance', 'month' keys
        previous_month: Dict with 'income', 'expenses', 'balance', 'month' keys

    Returns:
        PNG image bytes
    """
    categories = ['Receitas', 'Despesas', 'Saldo']

    current_values = [
        current_month.get('income', 0),
        current_month.get('expenses', 0),
        current_month.get('balance', 0)
    ]

    previous_values = [
        previous_month.get('income', 0),
        previous_month.get('expenses', 0),
        previous_month.get('balance', 0)
    ]

    x = range(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar([i - width/2 for i in x], previous_values,
                    width, label=previous_month.get('month', 'Mês Anterior'),
                    color='#95a5a6')
    bars2 = ax.bar([i + width/2 for i in x], current_values,
                    width, label=current_month.get('month', 'Mês Atual'),
                    color='#3498db')

    ax.set_ylabel('Valor (R$)', fontsize=12)
    ax.set_title('Comparação Mensal', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

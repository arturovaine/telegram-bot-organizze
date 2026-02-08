# Organizze API - Complete Documentation

## Overview

This document provides a complete reference for the Organizze API integration implemented in this bot.

**Base URL**: `https://api.organizze.com.br/rest/v2`
**Authentication**: HTTP Basic Auth (email + API key)
**Client Implementation**: `organizze_client.py`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Bank Accounts](#bank-accounts)
4. [Categories](#categories)
5. [Credit Cards](#credit-cards)
6. [Credit Card Invoices](#credit-card-invoices)
7. [Transactions](#transactions)
8. [Transfers](#transfers)
9. [Budgets](#budgets)
10. [Error Handling](#error-handling)
11. [Usage Examples](#usage-examples)

---

## Authentication

### Setup

```python
from organizze_client import OrganizzeClient

# Using environment variables (recommended)
client = OrganizzeClient()

# Or explicit credentials
client = OrganizzeClient(
    email="your-email@example.com",
    api_key="your-api-key-here"
)
```

### Required Environment Variables

- `ORGANIZZE_EMAIL` - Your Organizze account email
- `ORGANIZZE_API_KEY` - API token from https://app.organizze.com.br/configuracoes/api-keys

---

## Users

### Get User Details

```python
user = client.get_user(user_id=3)
```

**Response**:
```json
{
  "id": 3,
  "name": "João Silva",
  "email": "joao@example.com",
  "role": "admin"
}
```

---

## Bank Accounts

### List All Accounts

```python
accounts = client.get_accounts()
```

**Response**: List of account objects with `id`, `name`, `type`, `default_balance`, `archived`, etc.

### Get Specific Account

```python
account = client.get_account(account_id=123)
```

### Create Account

```python
new_account = client.create_account(
    name="Nubank",
    account_type="checking",  # checking, savings, other
    default_balance=1000.00,  # Initial balance in reais
    archived=False
)
```

### Update Account

```python
updated = client.update_account(
    account_id=123,
    name="Nubank Conta Corrente",
    default_balance=1500.00
)
```

### Delete Account

```python
client.delete_account(account_id=123)
```

---

## Categories

### List All Categories

```python
categories = client.get_categories()
```

**Response**: List with `id`, `name`, `color`, `parent_id`

### Get Specific Category

```python
category = client.get_category(category_id=42)
```

### Create Category

```python
new_category = client.create_category(
    name="Streaming",
    color="#FF5733"  # Hex color code
)
```

### Update Category

```python
updated = client.update_category(
    category_id=42,
    name="Serviços de Streaming",
    color="#FF0000"
)
```

### Delete Category

```python
# Delete and optionally reassign transactions to another category
client.delete_category(
    category_id=42,
    replacement_category_id=10  # Optional
)
```

---

## Credit Cards

### List All Credit Cards

```python
cards = client.get_credit_cards()
```

### Get Specific Card

```python
card = client.get_credit_card(card_id=456)
```

### Create Credit Card

```python
new_card = client.create_credit_card(
    name="Nubank",
    network="mastercard",  # visa, mastercard, amex, etc.
    closing_day=20,        # Invoice closing day
    due_day=27,            # Payment due day
    limit=5000.00,         # Credit limit in reais
    archived=False
)
```

### Update Credit Card

```python
updated = client.update_credit_card(
    card_id=456,
    name="Nubank Gold",
    limit=10000.00,
    closing_day=25,
    update_invoices_since="2025-01-01"  # Recalculate invoices from this date
)
```

### Delete Credit Card

```python
client.delete_credit_card(card_id=456)
```

---

## Credit Card Invoices

### List Invoices

```python
# Get all invoices for a year
invoices = client.get_invoices(
    card_id=456,
    year=2025
)

# Get invoices for a date range
invoices = client.get_invoices(
    card_id=456,
    start_date="2025-01-01",
    end_date="2025-12-31"
)
```

**Response**: List with `id`, `date`, `amount_cents`, `balance_cents`, `payment_amount_cents`

### Get Invoice Details

```python
invoice = client.get_invoice(
    card_id=456,
    invoice_id=789
)
```

**Response**: Full invoice with included transactions and payments

### Pay Invoice

```python
payment = client.pay_invoice(
    card_id=456,
    invoice_id=789,
    amount=1500.00,         # Payment amount in reais
    payment_date="2025-02-27",  # Optional, defaults to today
    account_id=123          # Optional, account used for payment
)
```

---

## Transactions

### List Transactions

```python
# Current month (default)
transactions = client.get_transactions()

# Specific date range
transactions = client.get_transactions(
    start_date="2025-01-01",
    end_date="2025-01-31"
)

# Filter by account
transactions = client.get_transactions(
    start_date="2025-01-01",
    end_date="2025-01-31",
    account_id=123
)
```

### Get Specific Transaction

```python
transaction = client.get_transaction(transaction_id=9999)
```

### Create Single Transaction

```python
# Expense (negative amount)
expense = client.create_transaction(
    description="Almoço no restaurante",
    date="2025-02-08",
    amount=-50.00,          # Negative for expense
    category_id=15,
    account_id=123,         # For bank account
    notes="Almoço de trabalho",
    tags=["trabalho", "reembolsável"]
)

# Income (positive amount)
income = client.create_transaction(
    description="Salário",
    date="2025-02-05",
    amount=5000.00,         # Positive for income
    category_id=1,
    account_id=123
)

# Credit card expense
cc_expense = client.create_transaction(
    description="Compras online",
    date="2025-02-08",
    amount=-200.00,
    category_id=10,
    credit_card_id=456      # Use credit card instead of account
)
```

### Create Recurring Transaction

```python
recurring = client.create_recurring_transaction(
    description="Netflix",
    start_date="2025-02-01",
    amount=-45.90,
    category_id=20,
    periodicity="monthly",  # monthly, yearly, weekly, biweekly, bimonthly, trimonthly
    occurrences=12,         # Optional, None = indefinite
    credit_card_id=456
)
```

### Update Transaction

```python
# Update single transaction
updated = client.update_transaction(
    transaction_id=9999,
    description="Almoço atualizado",
    amount=-55.00,
    category_id=16
)

# Update recurring transaction - all future occurrences
updated = client.update_transaction(
    transaction_id=9999,
    amount=-49.90,
    update_future=True
)

# Update recurring transaction - all occurrences
updated = client.update_transaction(
    transaction_id=9999,
    category_id=25,
    update_all=True
)
```

### Delete Transaction

```python
# Delete single transaction
client.delete_transaction(transaction_id=9999)

# Delete recurring - all future occurrences
client.delete_transaction(
    transaction_id=9999,
    delete_future=True
)

# Delete recurring - all occurrences
client.delete_transaction(
    transaction_id=9999,
    delete_all=True
)
```

---

## Transfers

### List Transfers

```python
# All transfers
transfers = client.get_transfers()

# Date range
transfers = client.get_transfers(
    start_date="2025-01-01",
    end_date="2025-01-31"
)
```

### Get Specific Transfer

```python
transfer = client.get_transfer(transfer_id=555)
```

### Create Transfer

```python
transfer = client.create_transfer(
    amount=500.00,              # Amount in reais (positive)
    date="2025-02-08",
    from_account_id=123,        # Source account
    to_account_id=456,          # Destination account
    description="Transferência entre contas",
    notes="Reserva de emergência",
    tags=["poupança"]
)
```

**Note**: Transfers only work between bank accounts, NOT credit cards

### Update Transfer

```python
# Can only update description, notes, and tags
updated = client.update_transfer(
    transfer_id=555,
    description="Nova descrição",
    notes="Novas observações",
    tags=["atualizado"]
)
```

### Delete Transfer

```python
client.delete_transfer(transfer_id=555)
```

---

## Budgets

### Get Budgets

```python
# Current month budgets
budgets = client.get_budgets()

# Specific year
budgets = client.get_budgets(year=2025)

# Specific month
budgets = client.get_budgets(year=2025, month=2)
```

**Response**: List with `category_id`, `amount_cents`, `predicted`, `actual`

---

## Error Handling

### Exception Types

```python
from organizze_client import (
    OrganizzeAPIError,      # Base exception
    OrganizzeAuthError,     # 401 - Invalid credentials
    OrganizzeValidationError # 422 - Validation error
)

try:
    transactions = client.get_transactions()
except OrganizzeAuthError:
    print("Invalid credentials!")
except OrganizzeValidationError as e:
    print(f"Validation errors: {e.errors}")
except OrganizzeAPIError as e:
    print(f"API error: {e}")
```

### Validation Errors (422)

```python
try:
    client.create_account(name="")  # Invalid: empty name
except OrganizzeValidationError as e:
    print(e.errors)  # {'name': ['Name cannot be empty']}
```

---

## Usage Examples

### Example 1: Monthly Financial Summary

```python
from datetime import datetime
from organizze_client import OrganizzeClient

client = OrganizzeClient()
today = datetime.now()

# Get data
accounts = client.get_accounts()
transactions = client.get_transactions(
    start_date=today.replace(day=1).strftime('%Y-%m-%d'),
    end_date=today.strftime('%Y-%m-%d')
)

# Calculate totals
total_balance = sum(
    acc['default_balance']
    for acc in accounts
    if not acc.get('archived')
)

income = sum(
    t['amount_cents'] / 100
    for t in transactions
    if t['amount_cents'] > 0
)

expenses = sum(
    abs(t['amount_cents']) / 100
    for t in transactions
    if t['amount_cents'] < 0
)

print(f"Balance: R$ {total_balance:,.2f}")
print(f"Income: R$ {income:,.2f}")
print(f"Expenses: R$ {expenses:,.2f}")
print(f"Net: R$ {income - expenses:,.2f}")
```

### Example 2: Create Expense and Tag It

```python
# Record a meal expense
expense = client.create_transaction(
    description="Almoço - Restaurante Japonês",
    date="2025-02-08",
    amount=-85.50,
    category_id=15,  # Alimentação category
    account_id=123,
    notes="Reunião com cliente importante",
    tags=["trabalho", "reembolsável", "cliente-xpto"]
)

print(f"Created expense ID: {expense['id']}")
```

### Example 3: Budget Progress Tracking

```python
from datetime import datetime

client = OrganizzeClient()
today = datetime.now()

# Get budgets and transactions
budgets = client.get_budgets(today.year, today.month)
transactions = client.get_transactions(
    start_date=today.replace(day=1).strftime('%Y-%m-%d'),
    end_date=today.strftime('%Y-%m-%d')
)
categories = client.get_categories()
cat_map = {c['id']: c['name'] for c in categories}

# Group expenses by category
cat_spending = {}
for t in transactions:
    if t['amount_cents'] < 0:
        cat_id = t.get('category_id')
        cat_spending[cat_id] = cat_spending.get(cat_id, 0) + abs(t['amount_cents'])

# Compare with budgets
for budget in budgets:
    cat_id = budget['category_id']
    cat_name = cat_map.get(cat_id, 'Unknown')
    budget_amount = budget['amount_cents'] / 100
    spent = cat_spending.get(cat_id, 0) / 100
    progress = (spent / budget_amount * 100) if budget_amount > 0 else 0

    status = "🟢" if progress < 80 else "🟡" if progress < 100 else "🔴"
    print(f"{status} {cat_name}: R$ {spent:.2f} / R$ {budget_amount:.2f} ({progress:.0f}%)")
```

### Example 4: Invoice Payment Workflow

```python
# Get current month invoice
card_id = 456
invoices = client.get_invoices(card_id, year=2025)
current_invoice = invoices[0]  # Most recent

invoice_details = client.get_invoice(card_id, current_invoice['id'])

print(f"Invoice for {invoice_details['date']}")
print(f"Amount: R$ {invoice_details['amount_cents'] / 100:,.2f}")
print(f"Due: {invoice_details['closing_date']}")

# Record payment
if input("Pay invoice? (y/n): ") == 'y':
    payment = client.pay_invoice(
        card_id=card_id,
        invoice_id=current_invoice['id'],
        amount=invoice_details['amount_cents'] / 100,
        account_id=123  # Account to debit from
    )
    print("✅ Payment recorded!")
```

---

## Rate Limits & Best Practices

1. **No official rate limits documented**, but be respectful
2. **Cache data** when possible to reduce API calls
3. **Use date ranges** to limit transaction queries
4. **Handle errors gracefully** - API can timeout or fail
5. **Always use HTTPS** - API only accepts secure connections
6. **Set User-Agent** - Required header (automatically set by client)

---

## Testing

Run the comprehensive test suite:

```bash
python test_api.py
```

This will test all read endpoints and verify your integration.

---

## Resources

- Official API Docs: https://github.com/organizze/api-doc
- Get API Key: https://app.organizze.com.br/configuracoes/api-keys
- Support: Contact Organizze support team

---

**Last Updated**: February 2026
**API Version**: v2
**Client Version**: 2.0

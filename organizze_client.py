"""
Organizze API Client - Complete implementation of all endpoints
Documentation: https://github.com/organizze/api-doc
"""

import os
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class OrganizzeAPIError(Exception):
    """Base exception for Organizze API errors"""
    pass


class OrganizzeAuthError(OrganizzeAPIError):
    """Authentication failed (401)"""
    pass


class OrganizzeValidationError(OrganizzeAPIError):
    """Validation error (422)"""
    def __init__(self, message: str, errors: Dict[str, List[str]]):
        super().__init__(message)
        self.errors = errors


class OrganizzeClient:
    """Complete Organizze API v2 client with all endpoints"""

    BASE_URL = "https://api.organizze.com.br/rest/v2"

    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Organizze API client

        Args:
            email: Organizze account email (defaults to ORGANIZZE_EMAIL env var)
            api_key: API token (defaults to ORGANIZZE_API_KEY env var)
        """
        self.email = email or os.environ.get('ORGANIZZE_EMAIL')
        self.api_key = api_key or os.environ.get('ORGANIZZE_API_KEY')

        if not self.email or not self.api_key:
            raise OrganizzeAPIError("Email and API key are required")

        self.auth = (self.email, self.api_key)
        self.headers = {
            'User-Agent': 'OrganizzeBot/2.0 (contact@organizzebot.com)',
            'Content-Type': 'application/json'
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Any]:
        """
        Make HTTP request to Organizze API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/accounts')
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response or None

        Raises:
            OrganizzeAuthError: Authentication failed
            OrganizzeValidationError: Validation error with field details
            OrganizzeAPIError: Other API errors
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=self.headers,
                timeout=30,
                **kwargs
            )

            # Log request for debugging
            logger.debug(f"{method} {endpoint} -> {response.status_code}")

            # Handle success
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204:  # No content
                    return None
                return response.json()

            # Handle authentication error
            if response.status_code == 401:
                raise OrganizzeAuthError("Invalid credentials")

            # Handle validation error
            if response.status_code == 422:
                error_data = response.json()
                errors = error_data.get('errors', {})
                raise OrganizzeValidationError("Validation failed", errors)

            # Handle other errors
            logger.error(f"API error {response.status_code}: {response.text}")
            raise OrganizzeAPIError(f"API request failed: {response.status_code}")

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {endpoint}")
            raise OrganizzeAPIError("Request timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise OrganizzeAPIError(f"Request failed: {str(e)}")

    # ==================== USER ENDPOINTS ====================

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user details"""
        return self._request('GET', f'/users/{user_id}')

    # ==================== ACCOUNT ENDPOINTS ====================

    def get_accounts(self) -> List[Dict]:
        """List all bank accounts"""
        return self._request('GET', '/accounts') or []

    def get_account(self, account_id: int) -> Optional[Dict]:
        """Get specific account details"""
        return self._request('GET', f'/accounts/{account_id}')

    def create_account(
        self,
        name: str,
        account_type: str = "checking",
        default_balance: float = 0.0,
        **kwargs
    ) -> Optional[Dict]:
        """
        Create new bank account

        Args:
            name: Account name
            account_type: Type (checking, savings, other)
            default_balance: Initial balance in reais
            **kwargs: Additional fields (archived, etc.)
        """
        data = {
            'name': name,
            'type': account_type,
            'default_balance': int(default_balance * 100),  # Convert to cents
            **kwargs
        }
        return self._request('POST', '/accounts', json=data)

    def update_account(
        self,
        account_id: int,
        name: Optional[str] = None,
        default_balance: Optional[float] = None,
        **kwargs
    ) -> Optional[Dict]:
        """Update account details"""
        data = {}
        if name:
            data['name'] = name
        if default_balance is not None:
            data['default_balance'] = int(default_balance * 100)
        data.update(kwargs)

        return self._request('PUT', f'/accounts/{account_id}', json=data)

    def delete_account(self, account_id: int) -> None:
        """Delete account"""
        self._request('DELETE', f'/accounts/{account_id}')

    # ==================== CATEGORY ENDPOINTS ====================

    def get_categories(self) -> List[Dict]:
        """List all categories"""
        return self._request('GET', '/categories') or []

    def get_category(self, category_id: int) -> Optional[Dict]:
        """Get specific category details"""
        return self._request('GET', f'/categories/{category_id}')

    def create_category(
        self,
        name: str,
        color: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Create new category

        Args:
            name: Category name
            color: Hex color code (e.g., '#FF5733')
            **kwargs: Additional fields
        """
        data = {'name': name}
        if color:
            data['color'] = color
        data.update(kwargs)

        return self._request('POST', '/categories', json=data)

    def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        color: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict]:
        """Update category details"""
        data = {}
        if name:
            data['name'] = name
        if color:
            data['color'] = color
        data.update(kwargs)

        return self._request('PUT', f'/categories/{category_id}', json=data)

    def delete_category(
        self,
        category_id: int,
        replacement_category_id: Optional[int] = None
    ) -> None:
        """
        Delete category

        Args:
            category_id: Category to delete
            replacement_category_id: Optional category to reassign existing transactions
        """
        params = {}
        if replacement_category_id:
            params['replacement_category_id'] = replacement_category_id

        self._request('DELETE', f'/categories/{category_id}', params=params)

    # ==================== BUDGET ENDPOINTS ====================

    def get_budgets(self, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict]:
        """
        Get budgets/goals

        Args:
            year: Year (defaults to current)
            month: Month (1-12, optional)

        Returns:
            List of budget entries
        """
        if year and month:
            endpoint = f'/budgets/{year}/{month}'
        elif year:
            endpoint = f'/budgets/{year}'
        else:
            endpoint = '/budgets'

        return self._request('GET', endpoint) or []

    # ==================== CREDIT CARD ENDPOINTS ====================

    def get_credit_cards(self) -> List[Dict]:
        """List all credit cards"""
        return self._request('GET', '/credit_cards') or []

    def get_credit_card(self, card_id: int) -> Optional[Dict]:
        """Get specific credit card details"""
        return self._request('GET', f'/credit_cards/{card_id}')

    def create_credit_card(
        self,
        name: str,
        network: str,
        closing_day: int,
        due_day: int,
        limit: float = 0.0,
        **kwargs
    ) -> Optional[Dict]:
        """
        Create new credit card

        Args:
            name: Card name
            network: Card network (visa, mastercard, etc.)
            closing_day: Invoice closing day (1-31)
            due_day: Payment due day (1-31)
            limit: Credit limit in reais
            **kwargs: Additional fields
        """
        data = {
            'name': name,
            'network': network,
            'closing_day': closing_day,
            'due_day': due_day,
            'limit_cents': int(limit * 100),
            **kwargs
        }
        return self._request('POST', '/credit_cards', json=data)

    def update_credit_card(
        self,
        card_id: int,
        name: Optional[str] = None,
        closing_day: Optional[int] = None,
        due_day: Optional[int] = None,
        limit: Optional[float] = None,
        update_invoices_since: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Update credit card details

        Args:
            card_id: Card ID
            update_invoices_since: Date to recalculate invoices from (YYYY-MM-DD)
        """
        data = {}
        if name:
            data['name'] = name
        if closing_day:
            data['closing_day'] = closing_day
        if due_day:
            data['due_day'] = due_day
        if limit is not None:
            data['limit_cents'] = int(limit * 100)
        if update_invoices_since:
            data['update_invoices_since'] = update_invoices_since
        data.update(kwargs)

        return self._request('PUT', f'/credit_cards/{card_id}', json=data)

    def delete_credit_card(self, card_id: int) -> None:
        """Delete credit card"""
        self._request('DELETE', f'/credit_cards/{card_id}')

    # ==================== CREDIT CARD INVOICE ENDPOINTS ====================

    def get_invoices(
        self,
        card_id: int,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get credit card invoices

        Args:
            card_id: Credit card ID
            year: Year (optional)
            start_date: Start date YYYY-MM-DD (optional)
            end_date: End date YYYY-MM-DD (optional)
        """
        params = {}
        if year:
            params['year'] = year
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        return self._request('GET', f'/credit_cards/{card_id}/invoices', params=params) or []

    def get_invoice(self, card_id: int, invoice_id: int) -> Optional[Dict]:
        """Get specific invoice details with transactions"""
        return self._request('GET', f'/credit_cards/{card_id}/invoices/{invoice_id}')

    def pay_invoice(
        self,
        card_id: int,
        invoice_id: int,
        amount: float,
        payment_date: Optional[str] = None,
        account_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Record invoice payment

        Args:
            card_id: Credit card ID
            invoice_id: Invoice ID
            amount: Payment amount in reais
            payment_date: Payment date YYYY-MM-DD (defaults to today)
            account_id: Account used for payment
        """
        data = {
            'amount_cents': int(amount * 100),
        }
        if payment_date:
            data['date'] = payment_date
        if account_id:
            data['account_id'] = account_id

        return self._request(
            'POST',
            f'/credit_cards/{card_id}/invoices/{invoice_id}/payments',
            json=data
        )

    # ==================== TRANSACTION ENDPOINTS ====================

    def get_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get transactions

        Args:
            start_date: Start date YYYY-MM-DD (defaults to current month start)
            end_date: End date YYYY-MM-DD (defaults to current month end)
            account_id: Filter by account ID
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if account_id:
            params['account_id'] = account_id

        return self._request('GET', '/transactions', params=params) or []

    def get_transaction(self, transaction_id: int) -> Optional[Dict]:
        """Get specific transaction details"""
        return self._request('GET', f'/transactions/{transaction_id}')

    def create_transaction(
        self,
        description: str,
        date: str,
        amount: float,
        category_id: int,
        account_id: Optional[int] = None,
        credit_card_id: Optional[int] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Create single transaction

        Args:
            description: Transaction description
            date: Date YYYY-MM-DD
            amount: Amount in reais (positive for income, negative for expense)
            category_id: Category ID
            account_id: Bank account ID (required if not credit card)
            credit_card_id: Credit card ID (required if not bank account)
            notes: Optional notes
            tags: Optional list of tags
            **kwargs: Additional fields
        """
        data = {
            'description': description,
            'date': date,
            'amount_cents': int(amount * 100),
            'category_id': category_id,
            **kwargs
        }

        if account_id:
            data['account_id'] = account_id
        if credit_card_id:
            data['credit_card_id'] = credit_card_id
        if notes:
            data['notes'] = notes
        if tags:
            data['tags'] = tags

        return self._request('POST', '/transactions', json=data)

    def create_recurring_transaction(
        self,
        description: str,
        start_date: str,
        amount: float,
        category_id: int,
        periodicity: str,
        occurrences: Optional[int] = None,
        account_id: Optional[int] = None,
        credit_card_id: Optional[int] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Create recurring transaction

        Args:
            description: Transaction description
            start_date: Start date YYYY-MM-DD
            amount: Amount in reais
            category_id: Category ID
            periodicity: monthly, yearly, weekly, biweekly, bimonthly, trimonthly
            occurrences: Number of occurrences (optional, defaults to indefinite)
            account_id: Bank account ID
            credit_card_id: Credit card ID
            **kwargs: Additional fields
        """
        data = {
            'description': description,
            'date': start_date,
            'amount_cents': int(amount * 100),
            'category_id': category_id,
            'periodicity': periodicity,
            **kwargs
        }

        if occurrences:
            data['occurrences'] = occurrences
        if account_id:
            data['account_id'] = account_id
        if credit_card_id:
            data['credit_card_id'] = credit_card_id

        return self._request('POST', '/transactions', json=data)

    def update_transaction(
        self,
        transaction_id: int,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        category_id: Optional[int] = None,
        date: Optional[str] = None,
        update_future: bool = False,
        update_all: bool = False,
        **kwargs
    ) -> Optional[Dict]:
        """
        Update transaction

        Args:
            transaction_id: Transaction ID
            description: New description
            amount: New amount in reais
            category_id: New category ID
            date: New date YYYY-MM-DD
            update_future: Apply changes to all future occurrences (recurring only)
            update_all: Apply changes to all occurrences (recurring only)
            **kwargs: Additional fields
        """
        data = {}
        if description:
            data['description'] = description
        if amount is not None:
            data['amount_cents'] = int(amount * 100)
        if category_id:
            data['category_id'] = category_id
        if date:
            data['date'] = date
        if update_future:
            data['update_future'] = True
        if update_all:
            data['update_all'] = True
        data.update(kwargs)

        return self._request('PUT', f'/transactions/{transaction_id}', json=data)

    def delete_transaction(
        self,
        transaction_id: int,
        delete_future: bool = False,
        delete_all: bool = False
    ) -> None:
        """
        Delete transaction

        Args:
            transaction_id: Transaction ID
            delete_future: Delete all future occurrences (recurring only)
            delete_all: Delete all occurrences (recurring only)
        """
        params = {}
        if delete_future:
            params['delete_future'] = 'true'
        if delete_all:
            params['delete_all'] = 'true'

        self._request('DELETE', f'/transactions/{transaction_id}', params=params)

    # ==================== TRANSFER ENDPOINTS ====================

    def get_transfers(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """Get transfers between accounts"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        return self._request('GET', '/transfers', params=params) or []

    def get_transfer(self, transfer_id: int) -> Optional[Dict]:
        """Get specific transfer details"""
        return self._request('GET', f'/transfers/{transfer_id}')

    def create_transfer(
        self,
        amount: float,
        date: str,
        from_account_id: int,
        to_account_id: int,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Create transfer between bank accounts

        Args:
            amount: Transfer amount in reais (positive)
            date: Transfer date YYYY-MM-DD
            from_account_id: Source account ID
            to_account_id: Destination account ID
            description: Optional description
            notes: Optional notes
            tags: Optional tags

        Note: Transfers only work between bank accounts, not credit cards
        """
        data = {
            'amount_cents': int(amount * 100),
            'date': date,
            'from_account_id': from_account_id,
            'to_account_id': to_account_id,
            **kwargs
        }

        if description:
            data['description'] = description
        if notes:
            data['notes'] = notes
        if tags:
            data['tags'] = tags

        return self._request('POST', '/transfers', json=data)

    def update_transfer(
        self,
        transfer_id: int,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Dict]:
        """Update transfer details (description, notes, tags only)"""
        data = {}
        if description:
            data['description'] = description
        if notes:
            data['notes'] = notes
        if tags:
            data['tags'] = tags
        data.update(kwargs)

        return self._request('PUT', f'/transfers/{transfer_id}', json=data)

    def delete_transfer(self, transfer_id: int) -> None:
        """Delete transfer"""
        self._request('DELETE', f'/transfers/{transfer_id}')

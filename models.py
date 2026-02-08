"""
Data models for Organizze API responses
Uses Pydantic for validation and type conversion
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    """User model"""
    id: int
    name: str
    email: str
    role: Optional[str] = None


class Account(BaseModel):
    """Bank account model"""
    id: int
    name: str
    type: str  # checking, savings, other
    default_balance: float = Field(alias='default_balance')
    archived: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('default_balance', mode='before')
    @classmethod
    def convert_balance(cls, v):
        """Convert cents to reais if needed"""
        if isinstance(v, int):
            return v / 100
        return v

    class Config:
        populate_by_name = True


class Category(BaseModel):
    """Category model"""
    id: int
    name: str
    color: Optional[str] = None
    parent_id: Optional[int] = None


class CreditCard(BaseModel):
    """Credit card model"""
    id: int
    name: str
    network: str
    closing_day: int
    due_day: int
    limit_cents: float = Field(alias='limit_cents')
    archived: bool = False
    default: bool = False

    @field_validator('limit_cents', mode='before')
    @classmethod
    def convert_limit(cls, v):
        """Convert cents to reais"""
        if isinstance(v, int):
            return v / 100
        return v

    @property
    def limit(self) -> float:
        """Get limit in reais"""
        return self.limit_cents

    class Config:
        populate_by_name = True


class Invoice(BaseModel):
    """Credit card invoice model"""
    id: int
    date: str
    starting_date: str
    closing_date: str
    amount_cents: float
    payment_amount_cents: float = 0
    balance_cents: float = 0
    previous_balance_cents: float = 0

    @field_validator('amount_cents', 'payment_amount_cents', 'balance_cents', 'previous_balance_cents', mode='before')
    @classmethod
    def convert_amounts(cls, v):
        """Convert cents to reais"""
        if isinstance(v, int):
            return v / 100
        return v

    @property
    def amount(self) -> float:
        return self.amount_cents

    @property
    def balance(self) -> float:
        return self.balance_cents

    @property
    def payment_amount(self) -> float:
        return self.payment_amount_cents


class Transaction(BaseModel):
    """Transaction model"""
    id: int
    description: str
    date: str
    amount_cents: float
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    credit_card_id: Optional[int] = None
    notes: Optional[str] = None
    attachments_count: int = 0
    tags: List[str] = Field(default_factory=list)
    paid: bool = True
    recurrence_id: Optional[int] = None
    oposite_transaction_id: Optional[int] = None
    oposite_account_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('amount_cents', mode='before')
    @classmethod
    def convert_amount(cls, v):
        """Convert cents to reais"""
        if isinstance(v, int):
            return v / 100
        return v

    @property
    def amount(self) -> float:
        """Get amount in reais"""
        return self.amount_cents

    @property
    def is_expense(self) -> bool:
        """Check if transaction is an expense"""
        return self.amount_cents < 0

    @property
    def is_income(self) -> bool:
        """Check if transaction is income"""
        return self.amount_cents > 0

    @property
    def absolute_amount(self) -> float:
        """Get absolute value of amount"""
        return abs(self.amount_cents)

    class Config:
        populate_by_name = True


class Transfer(BaseModel):
    """Transfer model"""
    id: int
    amount_cents: float
    date: str
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    from_account_id: int
    to_account_id: int
    from_transaction_id: int
    to_transaction_id: int

    @field_validator('amount_cents', mode='before')
    @classmethod
    def convert_amount(cls, v):
        """Convert cents to reais"""
        if isinstance(v, int):
            return v / 100
        return v

    @property
    def amount(self) -> float:
        return self.amount_cents


class Budget(BaseModel):
    """Budget/Goal model"""
    id: int
    category_id: int
    date: str
    amount_cents: float
    activity_type: int  # 1 for expense, 2 for income
    predicted: Optional[float] = None
    actual: Optional[float] = None

    @field_validator('amount_cents', mode='before')
    @classmethod
    def convert_amount(cls, v):
        """Convert cents to reais"""
        if isinstance(v, int):
            return v / 100
        return v

    @property
    def amount(self) -> float:
        return self.amount_cents

    @property
    def progress_percentage(self) -> float:
        """Calculate budget progress percentage"""
        if self.amount_cents == 0:
            return 0
        actual = self.actual or 0
        return (actual / self.amount_cents) * 100


class FinancialSummary(BaseModel):
    """Aggregated financial data for bot responses"""
    today: str
    month: str
    accounts: List[dict]
    total_balance: float
    income: float
    expenses: float
    balance: float
    recent_transactions: List[dict]
    credit_cards: List[dict]
    budgets: Optional[List[dict]] = None
    invoices: Optional[List[dict]] = None

    class Config:
        # Allow extra fields for extensibility
        extra = 'allow'

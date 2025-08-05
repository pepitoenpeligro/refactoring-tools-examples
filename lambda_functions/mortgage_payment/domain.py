"""
Domain layer for mortgage calculations following Domain-Driven Design principles.
Contains the core business entities and value objects.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


@dataclass(frozen=True)
class Money:
    """Value object representing a monetary amount with proper precision."""

    amount: Decimal
    currency: str = "EUR"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

        # Ensure 2 decimal places for currency
        object.__setattr__(self, 'amount', self.amount.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        ))

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} vs {other.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> 'Money':
        return Money(self.amount * factor, self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class InterestRate:
    """Value object representing an interest rate."""

    annual_percentage: Decimal

    def __post_init__(self):
        if self.annual_percentage < 0:
            raise ValueError("Interest rate cannot be negative")
        if self.annual_percentage > 100:
            raise ValueError("Interest rate cannot exceed 100%")

    @property
    def monthly_rate(self) -> Decimal:
        """Convert annual percentage to monthly decimal rate."""
        return (self.annual_percentage / 100) / 12

    @property
    def annual_decimal(self) -> Decimal:
        """Convert annual percentage to decimal."""
        return self.annual_percentage / 100

    def __str__(self) -> str:
        return f"{self.annual_percentage:.2f}%"


@dataclass(frozen=True)
class LoanTerm:
    """Value object representing the loan duration."""

    years: int

    def __post_init__(self):
        if self.years <= 0:
            raise ValueError("Loan term must be positive")
        if self.years > 50:
            raise ValueError("Loan term cannot exceed 50 years")

    @property
    def months(self) -> int:
        """Convert years to months."""
        return self.years * 12

    def __str__(self) -> str:
        return f"{self.years} years ({self.months} months)"


@dataclass(frozen=True)
class MortgageRequest:
    """Entity representing a mortgage loan request."""

    property_value: Money
    down_payment: Money
    loan_term: LoanTerm
    interest_rate: InterestRate

    def __post_init__(self):
        if self.down_payment.amount > self.property_value.amount:
            raise ValueError("Down payment cannot exceed property value")

        if self.property_value.currency != self.down_payment.currency:
            raise ValueError("Property value and down payment must be in same currency")

    @property
    def loan_amount(self) -> Money:
        """Calculate the actual loan amount after down payment."""
        return self.property_value - self.down_payment

    @property
    def loan_to_value_ratio(self) -> Decimal:
        """Calculate LTV ratio as percentage."""
        if self.property_value.amount == 0:
            return Decimal('0')
        return (self.loan_amount.amount / self.property_value.amount) * 100

    def __str__(self) -> str:
        return f"Mortgage: {self.loan_amount} at {self.interest_rate} for {self.loan_term}"


@dataclass(frozen=True)
class MonthlyPayment:
    """Entity representing the calculated monthly payment breakdown."""

    total_payment: Money
    principal_amount: Money
    interest_amount: Money
    month_number: int
    remaining_balance: Money

    def __post_init__(self):
        if self.month_number <= 0:
            raise ValueError("Month number must be positive")

        # Validate that principal + interest equals total (with small tolerance for rounding)
        calculated_total = self.principal_amount + self.interest_amount
        tolerance = Decimal('0.01')

        if abs(calculated_total.amount - self.total_payment.amount) > tolerance:
            raise ValueError("Principal + Interest must equal Total Payment")

    @property
    def principal_percentage(self) -> Decimal:
        """Calculate what percentage of payment goes to principal."""
        if self.total_payment.amount == 0:
            return Decimal('0')
        return (self.principal_amount.amount / self.total_payment.amount) * 100

    @property
    def interest_percentage(self) -> Decimal:
        """Calculate what percentage of payment goes to interest."""
        if self.total_payment.amount == 0:
            return Decimal('0')
        return (self.interest_amount.amount / self.total_payment.amount) * 100

    def __str__(self) -> str:
        return f"Month {self.month_number}: {self.total_payment} (P: {self.principal_amount}, I: {self.interest_amount})"


@dataclass(frozen=True)
class MortgageCalculationResult:
    """Entity representing the complete mortgage calculation result."""

    monthly_payment: Money
    total_interest: Money
    total_amount: Money
    mortgage_request: MortgageRequest

    @property
    def total_cost(self) -> Money:
        """Total cost including down payment."""
        return self.total_amount + self.mortgage_request.down_payment

    @property
    def interest_percentage_of_loan(self) -> Decimal:
        """Calculate what percentage of loan amount goes to interest."""
        if self.mortgage_request.loan_amount.amount == 0:
            return Decimal('0')
        return (self.total_interest.amount / self.mortgage_request.loan_amount.amount) * 100

    def __str__(self) -> str:
        return f"Monthly: {self.monthly_payment}, Total Interest: {self.total_interest}"

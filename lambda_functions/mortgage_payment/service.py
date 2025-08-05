"""
Application layer services for mortgage calculations.
Contains the business logic and use cases following hexagonal architecture.
"""

from decimal import Decimal
from typing import List
try:
    from domain import (
        Money, InterestRate, LoanTerm, MortgageRequest,
        MonthlyPayment, MortgageCalculationResult
    )
except ImportError:
    from .domain import (
        Money, InterestRate, LoanTerm, MortgageRequest,
        MonthlyPayment, MortgageCalculationResult
    )


class MortgageCalculatorService:
    """
    Service class containing the core business logic for mortgage calculations.
    Implements the use cases for mortgage payment calculations.
    """

    def calculate_monthly_payment(self, mortgage_request: MortgageRequest) -> Money:
        """
        Calculate the fixed monthly payment using the standard mortgage formula.

        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
        - M = Monthly payment
        - P = Principal loan amount
        - r = Monthly interest rate
        - n = Total number of payments (months)

        Args:
            mortgage_request: Complete mortgage request with all parameters

        Returns:
            Money object representing the monthly payment amount

        Raises:
            ValueError: If loan amount is zero or negative
        """
        print(f"Calculating monthly payment for loan: {mortgage_request.loan_amount}")

        principal = mortgage_request.loan_amount.amount

        if principal <= 0:
            raise ValueError("Loan amount must be positive")

        monthly_rate = mortgage_request.interest_rate.monthly_rate
        num_payments = mortgage_request.loan_term.months

        print(f"Principal: {principal}, Monthly rate: {monthly_rate}, Payments: {num_payments}")

        # Handle edge case: zero interest rate
        if monthly_rate == 0:
            monthly_payment = principal / num_payments
            print(f"Zero interest loan - monthly payment: {monthly_payment}")
        else:
            # Standard mortgage payment formula
            numerator = monthly_rate * (1 + monthly_rate) ** num_payments
            denominator = (1 + monthly_rate) ** num_payments - 1
            monthly_payment = principal * (numerator / denominator)
            print(f"Standard calculation - monthly payment: {monthly_payment}")

        return Money(monthly_payment, mortgage_request.loan_amount.currency)

    def calculate_total_interest(self, mortgage_request: MortgageRequest) -> Money:
        """
        Calculate the total interest paid over the life of the loan.

        Args:
            mortgage_request: Complete mortgage request with all parameters

        Returns:
            Money object representing total interest paid
        """
        print("Calculating total interest for mortgage")

        monthly_payment = self.calculate_monthly_payment(mortgage_request)
        total_payments = monthly_payment.amount * mortgage_request.loan_term.months
        total_interest = total_payments - mortgage_request.loan_amount.amount

        print(f"Total payments: {total_payments}, Total interest: {total_interest}")

        return Money(total_interest, mortgage_request.loan_amount.currency)

    def calculate_complete_mortgage(self, mortgage_request: MortgageRequest) -> MortgageCalculationResult:
        """
        Calculate complete mortgage information including monthly payment and total costs.

        Args:
            mortgage_request: Complete mortgage request with all parameters

        Returns:
            MortgageCalculationResult with all calculated values
        """
        print("Calculating complete mortgage breakdown")

        monthly_payment = self.calculate_monthly_payment(mortgage_request)
        total_interest = self.calculate_total_interest(mortgage_request)
        total_amount = mortgage_request.loan_amount + total_interest

        result = MortgageCalculationResult(
            monthly_payment=monthly_payment,
            total_interest=total_interest,
            total_amount=total_amount,
            mortgage_request=mortgage_request
        )

        print(f"Mortgage calculation complete: {result}")
        return result


class AmortizationService:
    """
    Service for calculating detailed amortization schedules.
    Provides month-by-month breakdown of payments.
    """

    def __init__(self, mortgage_calculator: MortgageCalculatorService):
        self.mortgage_calculator = mortgage_calculator

    def calculate_monthly_breakdown(self, mortgage_request: MortgageRequest, month: int) -> MonthlyPayment:
        """
        Calculate the payment breakdown for a specific month.

        Args:
            mortgage_request: Complete mortgage request
            month: Month number (1-based)

        Returns:
            MonthlyPayment object with detailed breakdown

        Raises:
            ValueError: If month is invalid
        """
        if month < 1 or month > mortgage_request.loan_term.months:
            raise ValueError(f"Month must be between 1 and {mortgage_request.loan_term.months}")

        print(f"Calculating payment breakdown for month {month}")

        monthly_payment_amount = self.mortgage_calculator.calculate_monthly_payment(mortgage_request)
        remaining_balance = self._calculate_remaining_balance(mortgage_request, month - 1)

        # Calculate interest for this month
        monthly_rate = mortgage_request.interest_rate.monthly_rate
        interest_amount = Money(
            remaining_balance.amount * monthly_rate,
            mortgage_request.loan_amount.currency
        )

        # Principal is the remainder
        principal_amount = monthly_payment_amount - interest_amount

        # Calculate remaining balance after this payment
        new_remaining_balance = remaining_balance - principal_amount

        print(f"Month {month}: Payment={monthly_payment_amount}, Principal={principal_amount}, Interest={interest_amount}")

        return MonthlyPayment(
            total_payment=monthly_payment_amount,
            principal_amount=principal_amount,
            interest_amount=interest_amount,
            month_number=month,
            remaining_balance=new_remaining_balance
        )

    def calculate_amortization_schedule(self, mortgage_request: MortgageRequest, max_months: int = None) -> List[MonthlyPayment]:
        """
        Calculate the complete amortization schedule.

        Args:
            mortgage_request: Complete mortgage request
            max_months: Maximum number of months to calculate (optional)

        Returns:
            List of MonthlyPayment objects for each month
        """
        total_months = mortgage_request.loan_term.months
        if max_months:
            total_months = min(total_months, max_months)

        print(f"Calculating amortization schedule for {total_months} months")

        schedule = []
        for month in range(1, total_months + 1):
            monthly_payment = self.calculate_monthly_breakdown(mortgage_request, month)
            schedule.append(monthly_payment)

        print(f"Amortization schedule calculated for {len(schedule)} months")
        return schedule

    def _calculate_remaining_balance(self, mortgage_request: MortgageRequest, months_paid: int) -> Money:
        """
        Calculate the remaining balance after a certain number of payments.

        Args:
            mortgage_request: Complete mortgage request
            months_paid: Number of months already paid

        Returns:
            Money object representing remaining balance
        """
        if months_paid <= 0:
            return mortgage_request.loan_amount

        if months_paid >= mortgage_request.loan_term.months:
            return Money(Decimal('0'), mortgage_request.loan_amount.currency)

        principal = mortgage_request.loan_amount.amount
        monthly_rate = mortgage_request.interest_rate.monthly_rate
        total_payments = mortgage_request.loan_term.months

        if monthly_rate == 0:
            # Simple calculation for zero interest
            monthly_payment = principal / total_payments
            remaining = principal - (monthly_payment * months_paid)
        else:
            # Standard remaining balance formula
            monthly_payment = self.mortgage_calculator.calculate_monthly_payment(mortgage_request).amount

            # Remaining balance formula
            numerator = (1 + monthly_rate) ** total_payments - (1 + monthly_rate) ** months_paid
            denominator = (1 + monthly_rate) ** total_payments - 1
            remaining = principal * (numerator / denominator)

        return Money(max(Decimal('0'), remaining), mortgage_request.loan_amount.currency)


class MortgageValidationService:
    """
    Service for validating mortgage requests and business rules.
    """

    @staticmethod
    def validate_mortgage_request(mortgage_request: MortgageRequest) -> None:
        """
        Validate that a mortgage request meets business requirements.

        Args:
            mortgage_request: Mortgage request to validate

        Raises:
            ValueError: If validation fails
        """
        print("Validating mortgage request")

        # Check minimum loan amount
        min_loan_amount = Money(Decimal('10000'), mortgage_request.loan_amount.currency)
        if mortgage_request.loan_amount.amount < min_loan_amount.amount:
            raise ValueError(f"Minimum loan amount is {min_loan_amount}")

        # Check maximum LTV ratio (typically 95%)
        max_ltv = Decimal('95')
        if mortgage_request.loan_to_value_ratio > max_ltv:
            raise ValueError(f"Loan-to-value ratio ({mortgage_request.loan_to_value_ratio:.2f}%) exceeds maximum ({max_ltv}%)")

        # Check reasonable interest rate range
        if mortgage_request.interest_rate.annual_percentage > Decimal('20'):
            raise ValueError("Interest rate seems unreasonably high (>20%)")

        print("Mortgage request validation passed")

    @staticmethod
    def validate_monthly_payment_affordability(mortgage_request: MortgageRequest, monthly_income: Money) -> bool:
        """
        Check if monthly payment is affordable based on income (typically 28% rule).

        Args:
            mortgage_request: Mortgage request
            monthly_income: Borrower's monthly income

        Returns:
            True if affordable, False otherwise
        """
        calculator = MortgageCalculatorService()
        monthly_payment = calculator.calculate_monthly_payment(mortgage_request)

        # 28% rule: mortgage payment should not exceed 28% of gross monthly income
        max_affordable = monthly_income * Decimal('0.28')

        is_affordable = monthly_payment.amount <= max_affordable.amount

        print(f"Affordability check: Payment {monthly_payment} vs Max {max_affordable} = {'PASS' if is_affordable else 'FAIL'}")

        return is_affordable

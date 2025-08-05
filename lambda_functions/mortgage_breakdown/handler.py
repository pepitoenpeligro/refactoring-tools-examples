"""
Infrastructure layer - Lambda handler for mortgage breakdown calculations.
This adapter provides detailed amortization schedules and monthly payment breakdowns.
"""

import json
from decimal import Decimal
from typing import Dict, Any, Optional, List

try:
    from domain import Money, InterestRate, LoanTerm, MortgageRequest, MonthlyPayment
    from service import MortgageCalculatorService, AmortizationService, MortgageValidationService
except ImportError:
    from .domain import Money, InterestRate, LoanTerm, MortgageRequest, MonthlyPayment
    from .service import MortgageCalculatorService, AmortizationService, MortgageValidationService


class MortgageBreakdownRequestAdapter:
    """
    Adapter to convert API Gateway request to domain objects for breakdown calculations.
    Handles input validation and transformation for amortization requests.
    """

    @staticmethod
    def from_event(event: Dict[str, Any]) -> tuple[MortgageRequest, Optional[int], Optional[int]]:
        """
        Convert Lambda event to MortgageRequest and breakdown parameters.

        Args:
            event: AWS Lambda event data

        Returns:
            Tuple of (MortgageRequest, specific_month, max_months)

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        print("Converting API event to MortgageBreakdown request")

        # Extract request body
        body = event.get('body')
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in request body")

        if not body:
            raise ValueError("Request body is required")

        # Extract and validate required parameters
        try:
            property_value_amount = MortgageBreakdownRequestAdapter._extract_decimal(
                body, 'property_value', 'Property value'
            )
            down_payment_amount = MortgageBreakdownRequestAdapter._extract_decimal(
                body, 'down_payment', 'Down payment'
            )
            loan_years = MortgageBreakdownRequestAdapter._extract_integer(
                body, 'loan_years', 'Loan years'
            )
            annual_interest_rate = MortgageBreakdownRequestAdapter._extract_decimal(
                body, 'interest_rate', 'Interest rate'
            )

            # Optional parameters for breakdown customization
            specific_month = body.get('month')  # For single month breakdown
            max_months = body.get('max_months', 12)  # Default to first year
            currency = body.get('currency', 'EUR')

            # Validate optional parameters
            if specific_month is not None:
                specific_month = int(specific_month)
                if specific_month < 1:
                    raise ValueError("Month must be 1 or greater")

            if max_months is not None:
                max_months = int(max_months)
                if max_months < 1 or max_months > loan_years * 12:
                    raise ValueError(f"Max months must be between 1 and {loan_years * 12}")

            print(f"Extracted values: property={property_value_amount}, down_payment={down_payment_amount}, "
                  f"years={loan_years}, rate={annual_interest_rate}%, month={specific_month}, max_months={max_months}")

            # Create domain objects
            property_value = Money(property_value_amount, currency)
            down_payment = Money(down_payment_amount, currency)
            loan_term = LoanTerm(loan_years)
            interest_rate = InterestRate(annual_interest_rate)

            mortgage_request = MortgageRequest(
                property_value=property_value,
                down_payment=down_payment,
                loan_term=loan_term,
                interest_rate=interest_rate
            )

            print(f"Created MortgageRequest: {mortgage_request}")
            return mortgage_request, specific_month, max_months

        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Invalid request parameters: {str(e)}")

    @staticmethod
    def _extract_decimal(data: Dict, key: str, field_name: str) -> Decimal:
        """Extract and validate decimal value from request data."""
        if key not in data:
            raise ValueError(f"{field_name} is required")

        try:
            value = Decimal(str(data[key]))
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")
            return value
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be a valid number")

    @staticmethod
    def _extract_integer(data: Dict, key: str, field_name: str) -> int:
        """Extract and validate integer value from request data."""
        if key not in data:
            raise ValueError(f"{field_name} is required")

        try:
            value = int(data[key])
            if value <= 0:
                raise ValueError(f"{field_name} must be positive")
            return value
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be a valid integer")


class MortgageBreakdownResponseAdapter:
    """
    Adapter to convert domain objects to API Gateway response format for breakdown results.
    Handles output transformation and formatting for amortization data.
    """

    @staticmethod
    def to_single_month_response(mortgage_request: MortgageRequest, monthly_payment: MonthlyPayment) -> Dict[str, Any]:
        """
        Convert single month breakdown to API response.

        Args:
            mortgage_request: Original mortgage request
            monthly_payment: Monthly payment breakdown

        Returns:
            API Gateway response dictionary
        """
        print(f"Creating single month response for month {monthly_payment.month_number}")

        response_data = {
            "calculation_type": "single_month_breakdown",
            "input_parameters": {
                "property_value": {
                    "amount": str(mortgage_request.property_value.amount),
                    "currency": mortgage_request.property_value.currency
                },
                "loan_amount": {
                    "amount": str(mortgage_request.loan_amount.amount),
                    "currency": mortgage_request.loan_amount.currency
                },
                "loan_term_years": mortgage_request.loan_term.years,
                "annual_interest_rate": str(mortgage_request.interest_rate.annual_percentage),
                "requested_month": monthly_payment.month_number
            },
            "month_breakdown": {
                "month_number": monthly_payment.month_number,
                "total_payment": {
                    "amount": str(monthly_payment.total_payment.amount),
                    "currency": monthly_payment.total_payment.currency
                },
                "principal_payment": {
                    "amount": str(monthly_payment.principal_amount.amount),
                    "currency": monthly_payment.principal_amount.currency,
                    "percentage": str(monthly_payment.principal_percentage.quantize(Decimal('0.01')))
                },
                "interest_payment": {
                    "amount": str(monthly_payment.interest_amount.amount),
                    "currency": monthly_payment.interest_amount.currency,
                    "percentage": str(monthly_payment.interest_percentage.quantize(Decimal('0.01')))
                },
                "remaining_balance": {
                    "amount": str(monthly_payment.remaining_balance.amount),
                    "currency": monthly_payment.remaining_balance.currency
                }
            },
            "summary": {
                "description": f"Payment breakdown for month {monthly_payment.month_number}",
                "principal_vs_interest": f"{monthly_payment.principal_percentage:.1f}% principal, {monthly_payment.interest_percentage:.1f}% interest",
                "remaining_balance": f"{monthly_payment.remaining_balance} remaining after this payment"
            }
        }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'X-Calculation-Type': 'mortgage-breakdown-single'
            },
            'body': json.dumps(response_data, indent=2)
        }

    @staticmethod
    def to_schedule_response(mortgage_request: MortgageRequest, schedule: List[MonthlyPayment]) -> Dict[str, Any]:
        """
        Convert amortization schedule to API response.

        Args:
            mortgage_request: Original mortgage request
            schedule: List of monthly payment breakdowns

        Returns:
            API Gateway response dictionary
        """
        print(f"Creating schedule response for {len(schedule)} months")

        # Calculate summary statistics
        total_principal = sum(payment.principal_amount.amount for payment in schedule)
        total_interest = sum(payment.interest_amount.amount for payment in schedule)
        total_payments = sum(payment.total_payment.amount for payment in schedule)

        schedule_data = []
        for payment in schedule:
            schedule_data.append({
                "month": payment.month_number,
                "total_payment": str(payment.total_payment.amount),
                "principal": str(payment.principal_amount.amount),
                "interest": str(payment.interest_amount.amount),
                "remaining_balance": str(payment.remaining_balance.amount),
                "principal_percentage": str(payment.principal_percentage.quantize(Decimal('0.1'))),
                "interest_percentage": str(payment.interest_percentage.quantize(Decimal('0.1')))
            })

        response_data = {
            "calculation_type": "amortization_schedule",
            "input_parameters": {
                "property_value": {
                    "amount": str(mortgage_request.property_value.amount),
                    "currency": mortgage_request.property_value.currency
                },
                "loan_amount": {
                    "amount": str(mortgage_request.loan_amount.amount),
                    "currency": mortgage_request.loan_amount.currency
                },
                "loan_term_years": mortgage_request.loan_term.years,
                "annual_interest_rate": str(mortgage_request.interest_rate.annual_percentage),
                "months_calculated": len(schedule)
            },
            "schedule_summary": {
                "total_payments": {
                    "amount": str(total_payments),
                    "currency": mortgage_request.loan_amount.currency
                },
                "total_principal": {
                    "amount": str(total_principal),
                    "currency": mortgage_request.loan_amount.currency
                },
                "total_interest": {
                    "amount": str(total_interest),
                    "currency": mortgage_request.loan_amount.currency
                },
                "average_monthly_payment": {
                    "amount": str(total_payments / len(schedule)),
                    "currency": mortgage_request.loan_amount.currency
                }
            },
            "payment_schedule": schedule_data,
            "analysis": {
                "first_month_interest_percentage": str(schedule[0].interest_percentage.quantize(Decimal('0.1'))) if schedule else "0",
                "last_month_interest_percentage": str(schedule[-1].interest_percentage.quantize(Decimal('0.1'))) if schedule else "0",
                "total_interest_vs_principal": f"{(total_interest/total_principal*100):.1f}% interest vs principal" if total_principal > 0 else "N/A"
            }
        }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'X-Calculation-Type': 'mortgage-breakdown-schedule',
                'X-Months-Calculated': str(len(schedule))
            },
            'body': json.dumps(response_data, indent=2)
        }

    @staticmethod
    def to_error_response(error_message: str, status_code: int = 400) -> Dict[str, Any]:
        """
        Convert error to API response format.

        Args:
            error_message: Error description
            status_code: HTTP status code

        Returns:
            API Gateway error response dictionary
        """
        print(f"Creating error response: {error_message}")

        error_data = {
            "error": "Mortgage breakdown calculation error",
            "message": error_message,
            "calculation_type": "mortgage_breakdown",
            "timestamp": "2025-01-01T00:00:00Z",
            "suggestions": [
                "Verify all input parameters are positive numbers",
                "Ensure property value is greater than down payment",
                "Check that interest rate is reasonable (0-20%)",
                "Confirm loan term is between 1-50 years",
                "If requesting specific month, ensure it's within loan term",
                "If requesting schedule, ensure max_months is reasonable"
            ]
        }

        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(error_data, indent=2)
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for mortgage breakdown calculations.
    Provides detailed amortization schedules and payment breakdowns.

    Args:
        event: AWS Lambda event data
        context: AWS Lambda context object

    Returns:
        API Gateway response format
    """
    try:
        print("Mortgage breakdown calculation Lambda started")
        print(f"Received event: {json.dumps(event)}")

        # Handle CORS preflight requests
        http_method = event.get('httpMethod', 'POST')
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': ''
            }

        # Convert event to domain objects (Infrastructure -> Domain)
        request_adapter = MortgageBreakdownRequestAdapter()
        mortgage_request, specific_month, max_months = request_adapter.from_event(event)

        print(f"Mortgage request created: {mortgage_request}")
        print(f"Breakdown parameters: month={specific_month}, max_months={max_months}")

        # Validate business rules (Application layer)
        validation_service = MortgageValidationService()
        validation_service.validate_mortgage_request(mortgage_request)

        print("Mortgage request validation passed")

        # Execute business logic (Application layer)
        calculator_service = MortgageCalculatorService()
        amortization_service = AmortizationService(calculator_service)

        response_adapter = MortgageBreakdownResponseAdapter()

        if specific_month is not None:
            # Calculate single month breakdown
            print(f"Calculating breakdown for specific month: {specific_month}")

            if specific_month > mortgage_request.loan_term.months:
                raise ValueError(f"Requested month {specific_month} exceeds loan term of {mortgage_request.loan_term.months} months")

            monthly_payment = amortization_service.calculate_monthly_breakdown(mortgage_request, specific_month)
            response = response_adapter.to_single_month_response(mortgage_request, monthly_payment)
        else:
            # Calculate amortization schedule
            print(f"Calculating amortization schedule for {max_months} months")
            schedule = amortization_service.calculate_amortization_schedule(mortgage_request, max_months)
            response = response_adapter.to_schedule_response(mortgage_request, schedule)

        print("Mortgage breakdown calculation completed successfully")
        return response

    except ValueError as e:
        print(f"Validation error in mortgage breakdown calculation: {str(e)}")
        return MortgageBreakdownResponseAdapter.to_error_response(str(e), 400)

    except Exception as e:
        print(f"Unexpected error in mortgage breakdown calculation: {str(e)}")
        return MortgageBreakdownResponseAdapter.to_error_response(
            "Internal server error during mortgage breakdown calculation", 500
        )

"""
Infrastructure layer - Lambda handler for mortgage payment calculations.
This is the adapter that connects AWS Lambda with our domain and application layers.
"""

import json
from decimal import Decimal
from typing import Dict, Any, Optional

try:
    from domain import Money, InterestRate, LoanTerm, MortgageRequest
    from service import MortgageCalculatorService, MortgageValidationService
except ImportError:
    from .domain import Money, InterestRate, LoanTerm, MortgageRequest
    from .service import MortgageCalculatorService, MortgageValidationService


class MortgagePaymentRequestAdapter:
    """
    Adapter to convert API Gateway request to domain objects.
    Handles input validation and transformation.
    """

    @staticmethod
    def from_event(event: Dict[str, Any]) -> MortgageRequest:
        """
        Convert Lambda event to MortgageRequest domain object.

        Args:
            event: AWS Lambda event data

        Returns:
            MortgageRequest domain object

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        print("Converting API event to MortgageRequest")

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
            property_value_amount = MortgagePaymentRequestAdapter._extract_decimal(
                body, 'property_value', 'Property value'
            )
            down_payment_amount = MortgagePaymentRequestAdapter._extract_decimal(
                body, 'down_payment', 'Down payment'
            )
            loan_years = MortgagePaymentRequestAdapter._extract_integer(
                body, 'loan_years', 'Loan years'
            )
            annual_interest_rate = MortgagePaymentRequestAdapter._extract_decimal(
                body, 'interest_rate', 'Interest rate'
            )

            # Optional currency parameter
            currency = body.get('currency', 'EUR')

            print(f"Extracted values: property={property_value_amount}, down_payment={down_payment_amount}, "
                  f"years={loan_years}, rate={annual_interest_rate}%, currency={currency}")

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
            return mortgage_request

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


class MortgagePaymentResponseAdapter:
    """
    Adapter to convert domain objects to API Gateway response format.
    Handles output transformation and formatting.
    """

    @staticmethod
    def to_success_response(mortgage_request: MortgageRequest, monthly_payment: Money) -> Dict[str, Any]:
        """
        Convert successful calculation to API response.

        Args:
            mortgage_request: Original mortgage request
            monthly_payment: Calculated monthly payment

        Returns:
            API Gateway response dictionary
        """
        print("Creating success response")

        # Calculate additional useful information
        calculator = MortgageCalculatorService()
        complete_result = calculator.calculate_complete_mortgage(mortgage_request)

        response_data = {
            "calculation_type": "monthly_payment",
            "input_parameters": {
                "property_value": {
                    "amount": str(mortgage_request.property_value.amount),
                    "currency": mortgage_request.property_value.currency
                },
                "down_payment": {
                    "amount": str(mortgage_request.down_payment.amount),
                    "currency": mortgage_request.down_payment.currency
                },
                "loan_amount": {
                    "amount": str(mortgage_request.loan_amount.amount),
                    "currency": mortgage_request.loan_amount.currency
                },
                "loan_term_years": mortgage_request.loan_term.years,
                "loan_term_months": mortgage_request.loan_term.months,
                "annual_interest_rate": str(mortgage_request.interest_rate.annual_percentage),
                "loan_to_value_ratio": str(mortgage_request.loan_to_value_ratio)
            },
            "results": {
                "monthly_payment": {
                    "amount": str(monthly_payment.amount),
                    "currency": monthly_payment.currency
                },
                "total_interest": {
                    "amount": str(complete_result.total_interest.amount),
                    "currency": complete_result.total_interest.currency
                },
                "total_amount_paid": {
                    "amount": str(complete_result.total_amount.amount),
                    "currency": complete_result.total_amount.currency
                },
                "total_cost_including_down_payment": {
                    "amount": str(complete_result.total_cost.amount),
                    "currency": complete_result.total_cost.currency
                },
                "interest_percentage_of_loan": str(complete_result.interest_percentage_of_loan)
            },
            "summary": {
                "description": f"Monthly payment of {monthly_payment} for {mortgage_request.loan_term}",
                "total_interest_cost": f"{complete_result.total_interest}",
                "effective_interest_rate": f"{complete_result.interest_percentage_of_loan:.2f}% of loan amount"
            }
        }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'X-Calculation-Type': 'mortgage-payment'
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
            "error": "Mortgage calculation error",
            "message": error_message,
            "calculation_type": "monthly_payment",
            "timestamp": "2025-01-01T00:00:00Z",  # In real scenario, use actual timestamp
            "suggestions": [
                "Verify all input parameters are positive numbers",
                "Ensure property value is greater than down payment",
                "Check that interest rate is reasonable (0-20%)",
                "Confirm loan term is between 1-50 years"
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
    AWS Lambda handler for mortgage payment calculations.
    Entry point that orchestrates the hexagonal architecture layers.

    Args:
        event: AWS Lambda event data
        context: AWS Lambda context object

    Returns:
        API Gateway response format
    """
    try:
        print("Mortgage payment calculation Lambda started")
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

        # Convert event to domain object (Infrastructure -> Domain)
        request_adapter = MortgagePaymentRequestAdapter()
        mortgage_request = request_adapter.from_event(event)

        print(f"Mortgage request created: {mortgage_request}")

        # Validate business rules (Application layer)
        validation_service = MortgageValidationService()
        validation_service.validate_mortgage_request(mortgage_request)

        print("Mortgage request validation passed")

        # Execute business logic (Application layer)
        calculator_service = MortgageCalculatorService()
        monthly_payment = calculator_service.calculate_monthly_payment(mortgage_request)

        print(f"Monthly payment calculated: {monthly_payment}")

        # Convert result to response (Domain -> Infrastructure)
        response_adapter = MortgagePaymentResponseAdapter()
        response = response_adapter.to_success_response(mortgage_request, monthly_payment)

        print("Mortgage payment calculation completed successfully")
        return response

    except ValueError as e:
        print(f"Validation error in mortgage payment calculation: {str(e)}")
        return MortgagePaymentResponseAdapter.to_error_response(str(e), 400)

    except Exception as e:
        print(f"Unexpected error in mortgage payment calculation: {str(e)}")
        return MortgagePaymentResponseAdapter.to_error_response(
            "Internal server error during mortgage calculation", 500
        )

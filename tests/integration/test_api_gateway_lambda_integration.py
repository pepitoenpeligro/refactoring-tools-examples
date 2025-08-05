#!/usr/bin/env python3

"""
Integration tests for API Gateway and Lambda functions.
These tests validate that the API Gateway correctly routes requests to the appropriate Lambda functions
and that the entire stack works end-to-end.
"""

import aws_cdk as cdk
from aws_cdk import (
    integ_tests_alpha as integ_tests,
    aws_apigateway as apigateway,
    assertions
)
from constructs import Construct
import json

from stacks.refactoring_tools_examples_stack import RefactoringToolsExamplesStack


class IntegrationTestStack(cdk.Stack):
    """Stack for integration testing the API Gateway and Lambda functions."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Deploy the main stack to test
        self.main_stack = RefactoringToolsExamplesStack(self, "TestStack")

        # Store the API for testing
        self.api = self.main_stack.children[0]  # Get the API Gateway from main stack


class ApiGatewayLambdaIntegrationTest:
    """Integration test class for API Gateway and Lambda functions."""

    def __init__(self):
        self.app = cdk.App()
        self.test_stack = IntegrationTestStack(self.app, "ApiGatewayLambdaIntegTest")

        # Create integration test construct
        self.integ_test = integ_tests.IntegTest(
            self.app, "ApiGatewayLambdaIntegration",
            test_cases=[self.test_stack],
            diff_assets=True,
            stack_update_workflow=True,
            cdk_command_options=integ_tests.CdkCommands(
                deploy=integ_tests.DeployOptions(
                    args=integ_tests.DeployArgs(
                        require_approval=integ_tests.RequireApproval.NEVER,
                        json=True
                    )
                ),
                destroy=integ_tests.DestroyOptions(
                    args=integ_tests.DestroyArgs(
                        force=True
                    )
                )
            )
        )

    def test_root_endpoint(self):
        """Test the root endpoint returns API information."""
        print("Testing root endpoint (GET /)")

        # Get API URL from stack outputs
        api_url = self.integ_test.assertions.aws_api_call(
            "CloudFormation", "describe_stacks",
            parameters={
                "StackName": self.test_stack.stack_name
            }
        ).at_path("Stacks.0.Outputs").expect(
            assertions.Matcher.any_value()
        )

        # Test root endpoint
        root_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/",
            method="GET"
        )

        # Validate response structure
        root_response.expect(
            assertions.Matcher.object_like({
                "service": assertions.Matcher.string_like_regexp(".*Hello.*Mortgage.*Service"),
                "version": assertions.Matcher.string_like_regexp("\\d+\\.\\d+\\.\\d+"),
                "endpoints": assertions.Matcher.array_with([
                    assertions.Matcher.object_like({
                        "path": "/",
                        "method": "GET"
                    }),
                    assertions.Matcher.object_like({
                        "path": "/hello",
                        "method": "GET"
                    }),
                    assertions.Matcher.object_like({
                        "path": "/mortgage/payment",
                        "method": "POST"
                    })
                ]),
                "status": "healthy"
            })
        )

        return root_response

    def test_hello_endpoint(self):
        """Test the hello endpoint returns random greetings."""
        print("Testing hello endpoint (GET /hello)")

        # Test basic hello
        hello_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/hello",
            method="GET"
        )

        hello_response.expect(
            assertions.Matcher.object_like({
                "greeting": assertions.Matcher.any_value(),
                "function": "hello-endpoint",
                "mood": assertions.Matcher.any_value()
            })
        )

        # Test hello with parameters
        hello_excited_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/hello?mood=excited&quote=true",
            method="GET"
        )

        hello_excited_response.expect(
            assertions.Matcher.object_like({
                "greeting": assertions.Matcher.any_value(),
                "mood": "excited",
                "daily_motivation": assertions.Matcher.any_value()
            })
        )

        return hello_response

    def test_hello_name_endpoint(self):
        """Test the personalized hello endpoint."""
        print("Testing hello name endpoint (GET /hello/{name})")

        # Test personalized greeting
        alice_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/hello/Alice",
            method="GET"
        )

        alice_response.expect(
            assertions.Matcher.object_like({
                "greeting": assertions.Matcher.string_like_regexp(".*Alice.*"),
                "name_analysis": assertions.Matcher.object_like({
                    "name": "Alice",
                    "length": 5,
                    "vowel_count": assertions.Matcher.any_value(),
                    "consonant_count": assertions.Matcher.any_value(),
                    "lucky_number": assertions.Matcher.any_value()
                }),
                "fun_facts": assertions.Matcher.array_with([
                    assertions.Matcher.any_value()
                ])
            })
        )

        # Test with style and language parameters
        maria_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/hello/Maria?style=formal&lang=es",
            method="GET"
        )

        maria_response.expect(
            assertions.Matcher.object_like({
                "greeting": assertions.Matcher.string_like_regexp(".*Maria.*"),
                "name_analysis": assertions.Matcher.object_like({
                    "name": "Maria"
                }),
                "processing_info": assertions.Matcher.object_like({
                    "style": "formal",
                    "language": "es"
                })
            })
        )

        return alice_response

    def test_mortgage_payment_endpoint(self):
        """Test the mortgage payment calculation endpoint."""
        print("Testing mortgage payment endpoint (POST /mortgage/payment)")

        # Test basic mortgage calculation
        mortgage_request = {
            "property_value": 300000,
            "down_payment": 60000,
            "loan_years": 30,
            "interest_rate": 3.5,
            "currency": "EUR"
        }

        payment_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/mortgage/payment",
            method="POST",
            headers={
                "Content-Type": "application/json"
            },
            body=json.dumps(mortgage_request)
        )

        payment_response.expect(
            assertions.Matcher.object_like({
                "calculation_type": "monthly_payment",
                "input_parameters": assertions.Matcher.object_like({
                    "property_value": assertions.Matcher.object_like({
                        "amount": "300000.00",
                        "currency": "EUR"
                    }),
                    "loan_amount": assertions.Matcher.object_like({
                        "amount": "240000.00",
                        "currency": "EUR"
                    }),
                    "loan_term_years": 30,
                    "annual_interest_rate": "3.50"
                }),
                "results": assertions.Matcher.object_like({
                    "monthly_payment": assertions.Matcher.object_like({
                        "amount": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "currency": "EUR"
                    }),
                    "total_interest": assertions.Matcher.object_like({
                        "amount": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "currency": "EUR"
                    })
                })
            })
        )

        # Test zero interest loan
        zero_interest_request = {
            "property_value": 200000,
            "down_payment": 40000,
            "loan_years": 20,
            "interest_rate": 0,
            "currency": "EUR"
        }

        zero_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/mortgage/payment",
            method="POST",
            headers={
                "Content-Type": "application/json"
            },
            body=json.dumps(zero_interest_request)
        )

        zero_response.expect(
            assertions.Matcher.object_like({
                "results": assertions.Matcher.object_like({
                    "monthly_payment": assertions.Matcher.object_like({
                        "amount": "666.67",  # 160000 / 240 months
                        "currency": "EUR"
                    })
                })
            })
        )

        return payment_response

    def test_mortgage_breakdown_endpoint(self):
        """Test the mortgage breakdown endpoint."""
        print("Testing mortgage breakdown endpoint (POST /mortgage/breakdown)")

        # Test single month breakdown
        single_month_request = {
            "property_value": 300000,
            "down_payment": 60000,
            "loan_years": 30,
            "interest_rate": 3.5,
            "month": 1,
            "currency": "EUR"
        }

        single_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/mortgage/breakdown",
            method="POST",
            headers={
                "Content-Type": "application/json"
            },
            body=json.dumps(single_month_request)
        )

        single_response.expect(
            assertions.Matcher.object_like({
                "calculation_type": "single_month_breakdown",
                "month_breakdown": assertions.Matcher.object_like({
                    "month_number": 1,
                    "total_payment": assertions.Matcher.object_like({
                        "amount": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "currency": "EUR"
                    }),
                    "principal_payment": assertions.Matcher.object_like({
                        "amount": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "percentage": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}")
                    }),
                    "interest_payment": assertions.Matcher.object_like({
                        "amount": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "percentage": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}")
                    }),
                    "remaining_balance": assertions.Matcher.object_like({
                        "amount": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "currency": "EUR"
                    })
                })
            })
        )

        # Test amortization schedule
        schedule_request = {
            "property_value": 250000,
            "down_payment": 50000,
            "loan_years": 25,
            "interest_rate": 4.0,
            "max_months": 6,
            "currency": "EUR"
        }

        schedule_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/mortgage/breakdown",
            method="POST",
            headers={
                "Content-Type": "application/json"
            },
            body=json.dumps(schedule_request)
        )

        schedule_response.expect(
            assertions.Matcher.object_like({
                "calculation_type": "amortization_schedule",
                "schedule_summary": assertions.Matcher.object_like({
                    "total_payments": assertions.Matcher.object_like({
                        "amount": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "currency": "EUR"
                    })
                }),
                "payment_schedule": assertions.Matcher.array_with([
                    assertions.Matcher.object_like({
                        "month": 1,
                        "total_payment": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "principal": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}"),
                        "interest": assertions.Matcher.string_like_regexp("\\d+\\.\\d{2}")
                    })
                ])
            })
        )

        # Validate that we have exactly 6 months
        schedule_response.at_path("payment_schedule").expect(
            assertions.Matcher.array_with([
                assertions.Matcher.object_like({"month": 1}),
                assertions.Matcher.object_like({"month": 2}),
                assertions.Matcher.object_like({"month": 3}),
                assertions.Matcher.object_like({"month": 4}),
                assertions.Matcher.object_like({"month": 5}),
                assertions.Matcher.object_like({"month": 6})
            ])
        )

        return schedule_response

    def test_error_handling(self):
        """Test error handling for invalid requests."""
        print("Testing error handling")

        # Test invalid mortgage request
        invalid_request = {
            "property_value": -100000,  # Negative value should fail
            "down_payment": 60000,
            "loan_years": 30,
            "interest_rate": 3.5
        }

        error_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/mortgage/payment",
            method="POST",
            headers={
                "Content-Type": "application/json"
            },
            body=json.dumps(invalid_request)
        )

        error_response.expect(
            assertions.Matcher.object_like({
                "error": assertions.Matcher.any_value(),
                "message": assertions.Matcher.string_like_regexp(".*negative.*"),
                "calculation_type": "monthly_payment"
            })
        )

        # Test missing required fields
        incomplete_request = {
            "property_value": 300000
            # Missing other required fields
        }

        missing_fields_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/mortgage/payment",
            method="POST",
            headers={
                "Content-Type": "application/json"
            },
            body=json.dumps(incomplete_request)
        )

        missing_fields_response.expect(
            assertions.Matcher.object_like({
                "error": assertions.Matcher.any_value(),
                "message": assertions.Matcher.string_like_regexp(".*required.*")
            })
        )

        return error_response

    def test_cors_headers(self):
        """Test that CORS headers are properly set."""
        print("Testing CORS headers")

        # Test OPTIONS request
        options_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/mortgage/payment",
            method="OPTIONS"
        )

        # Should return 200 with proper CORS headers
        options_response.expect(
            assertions.Matcher.object_like({
                "statusCode": 200
            })
        )

        # Test that actual requests have CORS headers
        hello_response = self.integ_test.assertions.http_api_call(
            url="${api_url}/hello",
            method="GET"
        )

        # Validate CORS headers are present in response
        hello_response.at_path("headers").expect(
            assertions.Matcher.object_like({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": assertions.Matcher.any_value(),
                "Access-Control-Allow-Methods": assertions.Matcher.any_value()
            })
        )

        return options_response

    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Running API Gateway Lambda Integration Tests")
        print("=" * 60)

        try:
            # Test all endpoints
            self.test_root_endpoint()
            self.test_hello_endpoint()
            self.test_hello_name_endpoint()
            self.test_mortgage_payment_endpoint()
            self.test_mortgage_breakdown_endpoint()
            self.test_error_handling()
            self.test_cors_headers()

            print("✅ All integration tests completed successfully!")

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            raise


def main():
    """Main function to run integration tests."""
    integration_test = ApiGatewayLambdaIntegrationTest()
    integration_test.run_all_tests()


if __name__ == "__main__":
    main()

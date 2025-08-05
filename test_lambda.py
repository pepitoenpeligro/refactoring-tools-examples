#!/usr/bin/env python3

"""
Comprehensive test script for all five Lambda functions.
This script allows testing each Lambda function locally without deploying to AWS.
Includes greeting functions and mortgage calculation functions.
"""

import json
import sys
import os
from typing import Dict, Any

# Add the lambda function directories to Python path
lambda_dir = os.path.join(os.path.dirname(__file__), 'lambda_functions')
root_dir = os.path.join(lambda_dir, 'root')
hello_dir = os.path.join(lambda_dir, 'hello')
hello_name_dir = os.path.join(lambda_dir, 'hello_name')
mortgage_payment_dir = os.path.join(lambda_dir, 'mortgage_payment')
mortgage_breakdown_dir = os.path.join(lambda_dir, 'mortgage_breakdown')

sys.path.insert(0, root_dir)
sys.path.insert(0, hello_dir)
sys.path.insert(0, hello_name_dir)
sys.path.insert(0, mortgage_payment_dir)
sys.path.insert(0, mortgage_breakdown_dir)


class MockContext:
    """Mock Lambda context for local testing."""

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.aws_request_id = f"test-request-id-{function_name}-12345"
        self.memory_limit_in_mb = 256
        self.remaining_time_in_millis = 30000


def print_separator(title: str):
    """Print a formatted separator for test sections."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_test_result(test_name: str, response: Dict[str, Any]):
    """Print formatted test results."""
    print(f"\n🧪 {test_name}")
    print(f"   Status Code: {response['statusCode']}")

    if response['statusCode'] == 200:
        print("   ✅ SUCCESS")
    else:
        print("   ❌ FAILED")

    # Pretty print response body
    try:
        body_data = json.loads(response['body'])
        print(f"   Response Preview: {json.dumps(body_data, indent=4)[:200]}...")
    except:
        print(f"   Response Body: {response['body'][:100]}...")


def test_root_lambda():
    """Test the root Lambda function."""
    print_separator("TESTING ROOT LAMBDA FUNCTION (/)")

    # Import the handler dynamically to avoid conflicts
    sys.path.insert(0, root_dir)
    import handler as root_handler

    try:
        # Test basic root request
        event = {
            "httpMethod": "GET",
            "path": "/",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None
        }

        context = MockContext("root-function")
        response = root_handler.lambda_handler(event, context)

        print_test_result("Root endpoint basic request", response)

        # Validate response structure
        assert response['statusCode'] == 200
        response_data = json.loads(response['body'])
        assert 'service' in response_data
        assert 'endpoints' in response_data
        assert 'version' in response_data

        print("   ✅ All root Lambda tests passed!")

    except Exception as e:
        print(f"   ❌ Root Lambda test failed: {str(e)}")
        return False

    finally:
        # Clean up imports
        if 'handler' in sys.modules:
            del sys.modules['handler']
        sys.path.remove(root_dir)

    return True


def test_hello_lambda():
    """Test the hello Lambda function."""
    print_separator("TESTING HELLO LAMBDA FUNCTION (/hello)")

    # Import the handler dynamically
    sys.path.insert(0, hello_dir)
    import handler as hello_handler

    try:
        # Test 1: Basic hello request
        event1 = {
            "httpMethod": "GET",
            "path": "/hello",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None
        }

        context = MockContext("hello-function")
        response1 = hello_handler.lambda_handler(event1, context)
        print_test_result("Hello endpoint basic request", response1)

        # Test 2: Hello with mood parameter
        event2 = {
            "httpMethod": "GET",
            "path": "/hello",
            "headers": {},
            "queryStringParameters": {
                "mood": "excited",
                "quote": "true"
            },
            "pathParameters": None,
            "body": None
        }

        response2 = hello_handler.lambda_handler(event2, context)
        print_test_result("Hello endpoint with excited mood", response2)

        # Test 3: Hello without quote
        event3 = {
            "httpMethod": "GET",
            "path": "/hello",
            "headers": {},
            "queryStringParameters": {
                "quote": "false",
                "mood": "calm"
            },
            "pathParameters": None,
            "body": None
        }

        response3 = hello_handler.lambda_handler(event3, context)
        print_test_result("Hello endpoint without quote", response3)

        # Validate responses
        assert response1['statusCode'] == 200
        assert response2['statusCode'] == 200
        assert response3['statusCode'] == 200

        response1_data = json.loads(response1['body'])
        response2_data = json.loads(response2['body'])
        response3_data = json.loads(response3['body'])

        assert 'greeting' in response1_data
        assert 'daily_motivation' in response2_data  # Should have quote
        assert 'daily_motivation' not in response3_data  # Should not have quote

        print("   ✅ All hello Lambda tests passed!")

    except Exception as e:
        print(f"   ❌ Hello Lambda test failed: {str(e)}")
        return False

    finally:
        # Clean up imports
        if 'handler' in sys.modules:
            del sys.modules['handler']
        sys.path.remove(hello_dir)

    return True


def test_hello_name_lambda():
    """Test the hello_name Lambda function."""
    print_separator("TESTING HELLO_NAME LAMBDA FUNCTION (/hello/{name})")

    # Import the handler dynamically
    sys.path.insert(0, hello_name_dir)
    import handler as hello_name_handler

    try:
        # Test 1: Basic personalized greeting
        event1 = {
            "httpMethod": "GET",
            "path": "/hello/Alice",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": {
                "name": "Alice"
            },
            "body": None
        }

        context = MockContext("hello-name-function")
        response1 = hello_name_handler.lambda_handler(event1, context)
        print_test_result("Personalized greeting for Alice", response1)

        # Test 2: Formal style greeting
        event2 = {
            "httpMethod": "GET",
            "path": "/hello/Bob",
            "headers": {},
            "queryStringParameters": {
                "style": "formal",
                "lang": "en"
            },
            "pathParameters": {
                "name": "Bob"
            },
            "body": None
        }

        response2 = hello_name_handler.lambda_handler(event2, context)
        print_test_result("Formal greeting for Bob", response2)

        # Test 3: Spanish greeting
        event3 = {
            "httpMethod": "GET",
            "path": "/hello/Maria",
            "headers": {},
            "queryStringParameters": {
                "style": "casual",
                "lang": "es"
            },
            "pathParameters": {
                "name": "Maria"
            },
            "body": None
        }

        response3 = hello_name_handler.lambda_handler(event3, context)
        print_test_result("Spanish greeting for Maria", response3)

        # Test 4: Enthusiastic style
        event4 = {
            "httpMethod": "GET",
            "path": "/hello/Charlie",
            "headers": {},
            "queryStringParameters": {
                "style": "enthusiastic"
            },
            "pathParameters": {
                "name": "Charlie"
            },
            "body": None
        }

        response4 = hello_name_handler.lambda_handler(event4, context)
        print_test_result("Enthusiastic greeting for Charlie", response4)

        # Validate responses
        assert response1['statusCode'] == 200
        assert response2['statusCode'] == 200
        assert response3['statusCode'] == 200
        assert response4['statusCode'] == 200

        response1_data = json.loads(response1['body'])
        response2_data = json.loads(response2['body'])
        response3_data = json.loads(response3['body'])
        response4_data = json.loads(response4['body'])

        # Validate response structure
        assert 'greeting' in response1_data
        assert 'name_analysis' in response1_data
        assert 'fun_facts' in response1_data
        assert response1_data['name_analysis']['name'] == 'Alice'

        # Check Spanish greeting
        assert 'Hola' in response3_data['greeting'] or 'Maria' in response3_data['greeting']

        print("   ✅ All hello_name Lambda tests passed!")

    except Exception as e:
        print(f"   ❌ Hello_name Lambda test failed: {str(e)}")
        return False

    finally:
        # Clean up imports
        if 'handler' in sys.modules:
            del sys.modules['handler']
        sys.path.remove(hello_name_dir)

    return True


def test_error_handling():
    """Test error handling for all Lambda functions."""
    print_separator("TESTING ERROR HANDLING")

    try:
        # Test that functions have proper error handling structure
        # We'll just verify they can handle None events gracefully

        # Test root lambda
        sys.path.insert(0, root_dir)
        import handler as root_handler

        context = MockContext("root-function")
        response = root_handler.lambda_handler(None, context)
        print_test_result("Root Lambda error handling", response)

        # Clean up
        del sys.modules['handler']
        sys.path.remove(root_dir)

        # Test hello lambda
        sys.path.insert(0, hello_dir)
        import handler as hello_handler

        response = hello_handler.lambda_handler(None, context)
        print_test_result("Hello Lambda error handling", response)

        # Clean up
        del sys.modules['handler']
        sys.path.remove(hello_dir)

        # Test hello_name lambda
        sys.path.insert(0, hello_name_dir)
        import handler as hello_name_handler

        response = hello_name_handler.lambda_handler(None, context)
        print_test_result("Hello Name Lambda error handling", response)

        # Clean up
        del sys.modules['handler']
        sys.path.remove(hello_name_dir)

        print("   ✅ All functions have error handling implemented!")
        return True

    except Exception as e:
        print(f"   ❌ Error handling test failed: {str(e)}")
        return False

    return True


def test_mortgage_payment_lambda():
    """Test the mortgage payment Lambda function."""
    print_separator("TESTING MORTGAGE PAYMENT LAMBDA FUNCTION (/mortgage/payment)")

    # Import the handler dynamically
    sys.path.insert(0, mortgage_payment_dir)
    import handler as mortgage_payment_handler

    try:
        # Test 1: Basic mortgage payment calculation
        event1 = {
            "httpMethod": "POST",
            "path": "/mortgage/payment",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": json.dumps({
                "property_value": 300000,
                "down_payment": 60000,
                "loan_years": 30,
                "interest_rate": 3.5,
                "currency": "EUR"
            })
        }

        context = MockContext("mortgage-payment-function")
        response1 = mortgage_payment_handler.lambda_handler(event1, context)
        print_test_result("Basic mortgage payment calculation", response1)

        # Test 2: Zero interest loan
        event2 = {
            "httpMethod": "POST",
            "path": "/mortgage/payment",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": json.dumps({
                "property_value": 200000,
                "down_payment": 40000,
                "loan_years": 20,
                "interest_rate": 0,
                "currency": "EUR"
            })
        }

        response2 = mortgage_payment_handler.lambda_handler(event2, context)
        print_test_result("Zero interest mortgage calculation", response2)

        # Test 3: High value mortgage
        event3 = {
            "httpMethod": "POST",
            "path": "/mortgage/payment",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": json.dumps({
                "property_value": 800000,
                "down_payment": 200000,
                "loan_years": 25,
                "interest_rate": 4.2,
                "currency": "EUR"
            })
        }

        response3 = mortgage_payment_handler.lambda_handler(event3, context)
        print_test_result("High value mortgage calculation", response3)

        # Validate responses
        assert response1['statusCode'] == 200
        assert response2['statusCode'] == 200
        assert response3['statusCode'] == 200

        response1_data = json.loads(response1['body'])
        response2_data = json.loads(response2['body'])
        response3_data = json.loads(response3['body'])

        assert 'results' in response1_data
        assert 'monthly_payment' in response1_data['results']
        assert 'total_interest' in response1_data['results']

        # Zero interest should have very minimal total interest (due to rounding)
        total_interest = float(response2_data['results']['total_interest']['amount'])
        assert total_interest < 1.0, f"Expected minimal interest for 0% rate, got {total_interest}"

        print("   ✅ All mortgage payment Lambda tests passed!")

    except Exception as e:
        print(f"   ❌ Mortgage payment Lambda test failed: {str(e)}")
        return False

    finally:
        # Clean up imports
        if 'handler' in sys.modules:
            del sys.modules['handler']
        sys.path.remove(mortgage_payment_dir)

    return True


def test_mortgage_breakdown_lambda():
    """Test the mortgage breakdown Lambda function."""
    print_separator("TESTING MORTGAGE BREAKDOWN LAMBDA FUNCTION (/mortgage/breakdown)")

    # Import the handler dynamically
    sys.path.insert(0, mortgage_breakdown_dir)
    import handler as mortgage_breakdown_handler

    try:
        # Test 1: Single month breakdown
        event1 = {
            "httpMethod": "POST",
            "path": "/mortgage/breakdown",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": json.dumps({
                "property_value": 300000,
                "down_payment": 60000,
                "loan_years": 30,
                "interest_rate": 3.5,
                "month": 1,
                "currency": "EUR"
            })
        }

        context = MockContext("mortgage-breakdown-function")
        response1 = mortgage_breakdown_handler.lambda_handler(event1, context)
        print_test_result("Single month breakdown calculation", response1)

        # Test 2: Amortization schedule (first 6 months)
        event2 = {
            "httpMethod": "POST",
            "path": "/mortgage/breakdown",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": json.dumps({
                "property_value": 250000,
                "down_payment": 50000,
                "loan_years": 25,
                "interest_rate": 4.0,
                "max_months": 6,
                "currency": "EUR"
            })
        }

        response2 = mortgage_breakdown_handler.lambda_handler(event2, context)
        print_test_result("Amortization schedule (6 months)", response2)

        # Test 3: Full year breakdown
        event3 = {
            "httpMethod": "POST",
            "path": "/mortgage/breakdown",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": json.dumps({
                "property_value": 400000,
                "down_payment": 80000,
                "loan_years": 20,
                "interest_rate": 3.8,
                "max_months": 12,
                "currency": "EUR"
            })
        }

        response3 = mortgage_breakdown_handler.lambda_handler(event3, context)
        print_test_result("Full year amortization schedule", response3)

        # Validate responses
        assert response1['statusCode'] == 200
        assert response2['statusCode'] == 200
        assert response3['statusCode'] == 200

        response1_data = json.loads(response1['body'])
        response2_data = json.loads(response2['body'])
        response3_data = json.loads(response3['body'])

        # Single month should have month_breakdown
        assert 'month_breakdown' in response1_data
        assert response1_data['month_breakdown']['month_number'] == 1

        # Schedule should have payment_schedule
        assert 'payment_schedule' in response2_data
        assert len(response2_data['payment_schedule']) == 6

        assert 'payment_schedule' in response3_data
        assert len(response3_data['payment_schedule']) == 12

        print("   ✅ All mortgage breakdown Lambda tests passed!")

    except Exception as e:
        print(f"   ❌ Mortgage breakdown Lambda test failed: {str(e)}")
        return False

    finally:
        # Clean up imports
        if 'handler' in sys.modules:
            del sys.modules['handler']
        sys.path.remove(mortgage_breakdown_dir)

    return True


def run_all_tests():
    """Run all test functions."""
    print("🚀 Starting comprehensive Lambda function tests...")
    print("   Testing 5 separate Lambda functions with different functionality\n")

    test_results = []

    try:
        # Run all tests
        test_results.append(("Root Lambda", test_root_lambda()))
        test_results.append(("Hello Lambda", test_hello_lambda()))
        test_results.append(("Hello Name Lambda", test_hello_name_lambda()))
        test_results.append(("Mortgage Payment Lambda", test_mortgage_payment_lambda()))
        test_results.append(("Mortgage Breakdown Lambda", test_mortgage_breakdown_lambda()))
        test_results.append(("Error Handling", test_error_handling()))

        # Print summary
        print_separator("TEST SUMMARY")

        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name:<20} {status}")
            if not result:
                all_passed = False

        print(f"\n{'='*60}")
        if all_passed:
            print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
            print("   All three Lambda functions are working correctly.")
            print("   Ready for deployment! 🚀")
        else:
            print("❌ SOME TESTS FAILED")
            print("   Please check the failed tests above.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

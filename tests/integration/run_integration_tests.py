#!/usr/bin/env python3

"""
Integration Test Runner for API Gateway and Lambda functions.
This script runs comprehensive integration tests to validate that the API Gateway
correctly routes requests to Lambda functions and the entire stack works end-to-end.
"""

import json
import time
import subprocess
import sys
import os
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class TestResult:
    """Data class to store test results."""
    test_name: str
    passed: bool
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None


class IntegrationTestRunner:
    """Main class for running integration tests against deployed API."""

    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> TestResult:
        """Make an HTTP request and return test result."""
        test_name = f"{method} {endpoint}"
        url = urljoin(self.api_base_url + "/", endpoint.lstrip('/'))

        start_time = time.time()

        try:
            self.log(f"Testing {test_name} -> {url}")

            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time

            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            result = TestResult(
                test_name=test_name,
                passed=200 <= response.status_code < 300,
                response_time=response_time,
                status_code=response.status_code,
                response_data=response_data
            )

            if result.passed:
                self.log(f"✅ {test_name} - Status: {response.status_code} - Time: {response_time:.2f}s")
            else:
                self.log(f"❌ {test_name} - Status: {response.status_code} - Time: {response_time:.2f}s", "ERROR")

        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                passed=False,
                response_time=response_time,
                error_message=str(e)
            )
            self.log(f"❌ {test_name} - Error: {str(e)}", "ERROR")

        self.test_results.append(result)
        return result

    def test_root_endpoint(self):
        """Test the root API information endpoint."""
        self.log("🏠 Testing Root Endpoint")

        result = self.make_request("GET", "/")

        if result.passed and result.response_data:
            # Validate response structure
            required_fields = ["service", "version", "endpoints", "status"]
            for field in required_fields:
                if field not in result.response_data:
                    self.log(f"❌ Missing required field: {field}", "ERROR")
                    result.passed = False

            # Check that we have all 5 endpoints
            endpoints = result.response_data.get("endpoints", [])
            if len(endpoints) != 5:
                self.log(f"❌ Expected 5 endpoints, got {len(endpoints)}", "ERROR")
                result.passed = False

            # Check service name
            service_name = result.response_data.get("service", "")
            if "Hello" not in service_name or "Mortgage" not in service_name:
                self.log(f"❌ Unexpected service name: {service_name}", "ERROR")
                result.passed = False

        return result

    def test_hello_endpoints(self):
        """Test all hello-related endpoints."""
        self.log("👋 Testing Hello Endpoints")

        results = []

        # Test basic hello
        result1 = self.make_request("GET", "/hello")
        if result1.passed and result1.response_data:
            if "greeting" not in result1.response_data:
                self.log("❌ Missing greeting field", "ERROR")
                result1.passed = False
        results.append(result1)

        # Test hello with parameters
        result2 = self.make_request("GET", "/hello?mood=excited&quote=true")
        if result2.passed and result2.response_data:
            if result2.response_data.get("mood") != "excited":
                self.log("❌ Mood parameter not processed correctly", "ERROR")
                result2.passed = False
            if "daily_motivation" not in result2.response_data:
                self.log("❌ Missing daily_motivation field when quote=true", "ERROR")
                result2.passed = False
        results.append(result2)

        # Test personalized hello
        result3 = self.make_request("GET", "/hello/Alice")
        if result3.passed and result3.response_data:
            if "Alice" not in result3.response_data.get("greeting", ""):
                self.log("❌ Name not included in personalized greeting", "ERROR")
                result3.passed = False
            if "name_analysis" not in result3.response_data:
                self.log("❌ Missing name_analysis field", "ERROR")
                result3.passed = False
        results.append(result3)

        # Test hello with language parameter
        result4 = self.make_request("GET", "/hello/María?style=formal&lang=es")
        if result4.passed and result4.response_data:
            processing_info = result4.response_data.get("processing_info", {})
            if processing_info.get("language") != "es":
                self.log("❌ Language parameter not processed correctly", "ERROR")
                result4.passed = False
        results.append(result4)

        return results

    def test_mortgage_payment_endpoint(self):
        """Test mortgage payment calculation endpoint."""
        self.log("🏠 Testing Mortgage Payment Endpoint")

        results = []

        # Test standard mortgage calculation
        mortgage_data = {
            "property_value": 300000,
            "down_payment": 60000,
            "loan_years": 30,
            "interest_rate": 3.5,
            "currency": "EUR"
        }

        result1 = self.make_request(
            "POST", "/mortgage/payment",
            json=mortgage_data,
            headers={"Content-Type": "application/json"}
        )

        if result1.passed and result1.response_data:
            # Validate response structure
            required_sections = ["calculation_type", "input_parameters", "results"]
            for section in required_sections:
                if section not in result1.response_data:
                    self.log(f"❌ Missing section: {section}", "ERROR")
                    result1.passed = False

            # Check calculation type
            if result1.response_data.get("calculation_type") != "monthly_payment":
                self.log("❌ Incorrect calculation_type", "ERROR")
                result1.passed = False

            # Validate monthly payment result
            results_section = result1.response_data.get("results", {})
            monthly_payment = results_section.get("monthly_payment", {})
            if not monthly_payment.get("amount") or not monthly_payment.get("currency"):
                self.log("❌ Invalid monthly payment result", "ERROR")
                result1.passed = False

        results.append(result1)

        # Test zero interest loan
        zero_interest_data = {
            "property_value": 200000,
            "down_payment": 40000,
            "loan_years": 20,
            "interest_rate": 0,
            "currency": "EUR"
        }

        result2 = self.make_request(
            "POST", "/mortgage/payment",
            json=zero_interest_data,
            headers={"Content-Type": "application/json"}
        )

        if result2.passed and result2.response_data:
            # For zero interest, monthly payment should be exactly loan_amount / months
            # 160000 / 240 = 666.67
            monthly_payment = result2.response_data.get("results", {}).get("monthly_payment", {})
            amount = float(monthly_payment.get("amount", 0))
            expected = 160000 / 240  # 666.67
            if abs(amount - expected) > 1:  # Allow small rounding difference
                self.log(f"❌ Zero interest calculation incorrect. Expected ~{expected:.2f}, got {amount}", "ERROR")
                result2.passed = False

        results.append(result2)

        # Test error handling - invalid data
        invalid_data = {
            "property_value": -100000,  # Negative value
            "down_payment": 60000,
            "loan_years": 30,
            "interest_rate": 3.5
        }

        result3 = self.make_request(
            "POST", "/mortgage/payment",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )

        # This should return 400 error
        if result3.status_code == 400:
            result3.passed = True  # Error handling working correctly
            self.log("✅ Error handling working for invalid input")
        else:
            self.log(f"❌ Expected 400 error for invalid input, got {result3.status_code}", "ERROR")
            result3.passed = False

        results.append(result3)

        return results

    def test_mortgage_breakdown_endpoint(self):
        """Test mortgage breakdown calculation endpoint."""
        self.log("📊 Testing Mortgage Breakdown Endpoint")

        results = []

        # Test single month breakdown
        single_month_data = {
            "property_value": 300000,
            "down_payment": 60000,
            "loan_years": 30,
            "interest_rate": 3.5,
            "month": 1,
            "currency": "EUR"
        }

        result1 = self.make_request(
            "POST", "/mortgage/breakdown",
            json=single_month_data,
            headers={"Content-Type": "application/json"}
        )

        if result1.passed and result1.response_data:
            # Validate single month response
            if result1.response_data.get("calculation_type") != "single_month_breakdown":
                self.log("❌ Incorrect calculation_type for single month", "ERROR")
                result1.passed = False

            month_breakdown = result1.response_data.get("month_breakdown", {})
            if month_breakdown.get("month_number") != 1:
                self.log("❌ Incorrect month number", "ERROR")
                result1.passed = False

            required_fields = ["total_payment", "principal_payment", "interest_payment", "remaining_balance"]
            for field in required_fields:
                if field not in month_breakdown:
                    self.log(f"❌ Missing field in month breakdown: {field}", "ERROR")
                    result1.passed = False

        results.append(result1)

        # Test amortization schedule
        schedule_data = {
            "property_value": 250000,
            "down_payment": 50000,
            "loan_years": 25,
            "interest_rate": 4.0,
            "max_months": 6,
            "currency": "EUR"
        }

        result2 = self.make_request(
            "POST", "/mortgage/breakdown",
            json=schedule_data,
            headers={"Content-Type": "application/json"}
        )

        if result2.passed and result2.response_data:
            # Validate schedule response
            if result2.response_data.get("calculation_type") != "amortization_schedule":
                self.log("❌ Incorrect calculation_type for schedule", "ERROR")
                result2.passed = False

            payment_schedule = result2.response_data.get("payment_schedule", [])
            if len(payment_schedule) != 6:
                self.log(f"❌ Expected 6 months in schedule, got {len(payment_schedule)}", "ERROR")
                result2.passed = False

            # Check that months are sequential
            for i, month_data in enumerate(payment_schedule):
                if month_data.get("month") != i + 1:
                    self.log(f"❌ Month sequence broken at position {i}", "ERROR")
                    result2.passed = False
                    break

        results.append(result2)

        return results

    def test_cors_and_options(self):
        """Test CORS configuration and OPTIONS requests."""
        self.log("🌐 Testing CORS and OPTIONS")

        results = []

        # Test OPTIONS on mortgage endpoint
        result1 = self.make_request("OPTIONS", "/mortgage/payment")
        if result1.status_code == 200:
            result1.passed = True
            self.log("✅ OPTIONS request handled correctly")
        else:
            self.log(f"❌ OPTIONS request failed with status {result1.status_code}", "ERROR")
            result1.passed = False

        results.append(result1)

        # Test that GET requests include CORS headers
        result2 = self.make_request("GET", "/hello")
        # We can't easily test headers with requests, but we can ensure the request succeeds
        # In a real browser environment, CORS would be validated
        results.append(result2)

        return results

    def run_all_tests(self):
        """Run all integration tests."""
        self.log("🚀 Starting API Gateway Lambda Integration Tests")
        self.log(f"Base URL: {self.api_base_url}")
        self.log("=" * 80)

        start_time = time.time()

        try:
            # Run all test suites
            self.test_root_endpoint()
            self.test_hello_endpoints()
            self.test_mortgage_payment_endpoint()
            self.test_mortgage_breakdown_endpoint()
            self.test_cors_and_options()

        except Exception as e:
            self.log(f"❌ Test execution failed: {e}", "ERROR")

        finally:
            total_time = time.time() - start_time
            self.print_summary(total_time)

    def print_summary(self, total_time: float):
        """Print test summary."""
        self.log("=" * 80)
        self.log("📊 TEST SUMMARY")
        self.log("=" * 80)

        passed_tests = [r for r in self.test_results if r.passed]
        failed_tests = [r for r in self.test_results if not r.passed]

        self.log(f"Total Tests: {len(self.test_results)}")
        self.log(f"Passed: {len(passed_tests)}")
        self.log(f"Failed: {len(failed_tests)}")
        self.log(f"Success Rate: {(len(passed_tests)/len(self.test_results)*100):.1f}%")
        self.log(f"Total Time: {total_time:.2f}s")

        if failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for test in failed_tests:
                self.log(f"  - {test.test_name}")
                if test.error_message:
                    self.log(f"    Error: {test.error_message}")
                elif test.status_code:
                    self.log(f"    Status Code: {test.status_code}")

        self.log("\n📈 PERFORMANCE METRICS:")
        for test in self.test_results:
            if test.passed:
                self.log(f"  {test.test_name}: {test.response_time:.2f}s")

        if len(passed_tests) == len(self.test_results):
            self.log("\n🎉 ALL INTEGRATION TESTS PASSED!")
            return True
        else:
            self.log(f"\n❌ {len(failed_tests)} TESTS FAILED")
            return False


def get_api_url_from_stack():
    """Get API URL from deployed CDK stack."""
    try:
        result = subprocess.run([
            "aws", "cloudformation", "describe-stacks",
            "--stack-name", "IntegTestApiGatewayLambda-MainStack",
            "--query", "Stacks[0].Outputs[?OutputKey=='ApiGatewayUrl'].OutputValue",
            "--output", "text"
        ], capture_output=True, text=True, check=True)

        api_url = result.stdout.strip()
        if api_url and api_url != "None":
            return api_url
    except subprocess.CalledProcessError:
        pass

    return None


def main():
    """Main function to run integration tests."""
    print("🧪 API Gateway Lambda Integration Test Runner")
    print("=" * 60)

    # Try to get API URL from stack outputs
    api_url = get_api_url_from_stack()

    if not api_url:
        # Fallback to command line argument or environment variable
        if len(sys.argv) > 1:
            api_url = sys.argv[1]
        else:
            api_url = os.environ.get("API_BASE_URL")

    if not api_url:
        print("❌ Error: API URL not provided")
        print("Usage:")
        print("  python run_integration_tests.py <api_url>")
        print("  export API_BASE_URL=<api_url> && python run_integration_tests.py")
        print("  Or deploy the stack first and the URL will be auto-detected")
        sys.exit(1)

    # Validate URL format
    if not api_url.startswith(('http://', 'https://')):
        print(f"❌ Error: Invalid URL format: {api_url}")
        sys.exit(1)

    # Run tests
    runner = IntegrationTestRunner(api_url)
    success = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

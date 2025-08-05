#!/usr/bin/env python3

"""
API Examples - Easy testing script for all Lambda endpoints
This script provides examples of how to call each API endpoint
"""

import json
import requests
from typing import Dict, Any

API_BASE_URL = "https://my-apigateway-id.execute-api.your-region.amazonaws.com/prod"

class APITester:
    """Helper class to test API endpoints"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def test_root_endpoint(self):
        """Test the root API information endpoint"""
        print("🏠 Testing Root Endpoint (/)")
        print("=" * 50)

        try:
            response = requests.get(f"{self.base_url}/")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Service: {data['service']}")
                print(f"Version: {data['version']}")
                print(f"Endpoints available: {len(data['endpoints'])}")
                print("Services:")
                for service_name, service_info in data.get('services', {}).items():
                    print(f"  - {service_name}: {service_info['description']}")
            else:
                print(f"Error: {response.text}")

        except Exception as e:
            print(f"Error calling root endpoint: {e}")

        print("\n")

    def test_hello_endpoint(self):
        """Test the hello endpoint with different moods"""
        print("👋 Testing Hello Endpoint (/hello)")
        print("=" * 50)

        test_cases = [
            {"params": {}, "description": "Basic hello"},
            {"params": {"mood": "excited", "quote": "true"}, "description": "Excited with quote"},
            {"params": {"mood": "calm", "quote": "false"}, "description": "Calm without quote"}
        ]

        for test_case in test_cases:
            print(f"Testing: {test_case['description']}")
            try:
                response = requests.get(f"{self.base_url}/hello", params=test_case["params"])
                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"Greeting: {data.get('greeting', 'N/A')}")
                    print(f"Mood: {data.get('mood', 'N/A')}")
                    if 'daily_motivation' in data:
                        print(f"Quote: {data['daily_motivation']}")
                else:
                    print(f"Error: {response.text}")

            except Exception as e:
                print(f"Error: {e}")

            print("-" * 30)

        print("\n")

    def test_hello_name_endpoint(self):
        """Test the personalized hello endpoint"""
        print("🎭 Testing Hello Name Endpoint (/hello/{name})")
        print("=" * 50)

        test_cases = [
            {"name": "Alice", "params": {}, "description": "Basic personalized greeting"},
            {"name": "María", "params": {"style": "formal", "lang": "es"}, "description": "Formal Spanish greeting"},
            {"name": "Charlie", "params": {"style": "enthusiastic"}, "description": "Enthusiastic greeting"},
            {"name": "Bob", "params": {"style": "poetic", "lang": "fr"}, "description": "Poetic French greeting"}
        ]

        for test_case in test_cases:
            print(f"Testing: {test_case['description']}")
            try:
                response = requests.get(
                    f"{self.base_url}/hello/{test_case['name']}",
                    params=test_case["params"]
                )
                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"Greeting: {data.get('greeting', 'N/A')}")
                    if 'name_analysis' in data:
                        analysis = data['name_analysis']
                        print(f"Name analysis: {analysis['vowel_count']} vowels, {analysis['consonant_count']} consonants")
                        print(f"Lucky number: {analysis['lucky_number']}")
                    if 'fun_facts' in data and data['fun_facts']:
                        print(f"Fun fact: {data['fun_facts'][0]}")
                else:
                    print(f"Error: {response.text}")

            except Exception as e:
                print(f"Error: {e}")

            print("-" * 30)

        print("\n")

    def test_mortgage_payment_endpoint(self):
        """Test the mortgage payment calculation endpoint"""
        print("🏠 Testing Mortgage Payment Endpoint (/mortgage/payment)")
        print("=" * 50)

        test_cases = [
            {
                "data": {
                    "property_value": 300000,
                    "down_payment": 60000,
                    "loan_years": 30,
                    "interest_rate": 3.5,
                    "currency": "EUR"
                },
                "description": "Standard 30-year mortgage"
            },
            {
                "data": {
                    "property_value": 200000,
                    "down_payment": 40000,
                    "loan_years": 20,
                    "interest_rate": 0,
                    "currency": "EUR"
                },
                "description": "Zero interest loan"
            },
            {
                "data": {
                    "property_value": 500000,
                    "down_payment": 100000,
                    "loan_years": 25,
                    "interest_rate": 4.2,
                    "currency": "EUR"
                },
                "description": "High-value property mortgage"
            }
        ]

        for test_case in test_cases:
            print(f"Testing: {test_case['description']}")
            try:
                response = requests.post(
                    f"{self.base_url}/mortgage/payment",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', {})

                    monthly_payment = results.get('monthly_payment', {})
                    total_interest = results.get('total_interest', {})

                    print(f"Monthly Payment: {monthly_payment.get('amount', 'N/A')} {monthly_payment.get('currency', '')}")
                    print(f"Total Interest: {total_interest.get('amount', 'N/A')} {total_interest.get('currency', '')}")
                    print(f"Interest % of Loan: {results.get('interest_percentage_of_loan', 'N/A')}%")

                    if 'summary' in data:
                        print(f"Summary: {data['summary'].get('description', 'N/A')}")
                else:
                    print(f"Error: {response.text}")

            except Exception as e:
                print(f"Error: {e}")

            print("-" * 30)

        print("\n")

    def test_mortgage_breakdown_endpoint(self):
        """Test the mortgage breakdown endpoint"""
        print("📊 Testing Mortgage Breakdown Endpoint (/mortgage/breakdown)")
        print("=" * 50)

        test_cases = [
            {
                "data": {
                    "property_value": 300000,
                    "down_payment": 60000,
                    "loan_years": 30,
                    "interest_rate": 3.5,
                    "month": 1,
                    "currency": "EUR"
                },
                "description": "Single month breakdown (Month 1)"
            },
            {
                "data": {
                    "property_value": 250000,
                    "down_payment": 50000,
                    "loan_years": 25,
                    "interest_rate": 4.0,
                    "max_months": 6,
                    "currency": "EUR"
                },
                "description": "First 6 months amortization schedule"
            },
            {
                "data": {
                    "property_value": 400000,
                    "down_payment": 80000,
                    "loan_years": 20,
                    "interest_rate": 3.8,
                    "max_months": 12,
                    "currency": "EUR"
                },
                "description": "Full year amortization schedule"
            }
        ]

        for test_case in test_cases:
            print(f"Testing: {test_case['description']}")
            try:
                response = requests.post(
                    f"{self.base_url}/mortgage/breakdown",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()

                    if 'month_breakdown' in data:
                        # Single month response
                        breakdown = data['month_breakdown']
                        print(f"Month {breakdown['month_number']}:")
                        print(f"  Total Payment: {breakdown['total_payment']['amount']} {breakdown['total_payment']['currency']}")
                        print(f"  Principal: {breakdown['principal_payment']['amount']} ({breakdown['principal_payment']['percentage']}%)")
                        print(f"  Interest: {breakdown['interest_payment']['amount']} ({breakdown['interest_payment']['percentage']}%)")
                        print(f"  Remaining: {breakdown['remaining_balance']['amount']}")

                    elif 'payment_schedule' in data:
                        # Schedule response
                        schedule = data['payment_schedule']
                        summary = data.get('schedule_summary', {})

                        print(f"Schedule for {len(schedule)} months:")
                        print(f"Total Payments: {summary.get('total_payments', {}).get('amount', 'N/A')}")
                        print(f"Total Interest: {summary.get('total_interest', {}).get('amount', 'N/A')}")

                        print("First 3 months:")
                        for i, month in enumerate(schedule[:3]):
                            print(f"  Month {month['month']}: Payment={month['total_payment']}, Principal={month['principal']}, Interest={month['interest']}")
                else:
                    print(f"Error: {response.text}")

            except Exception as e:
                print(f"Error: {e}")

            print("-" * 30)

        print("\n")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting comprehensive API testing...")
        print(f"Base URL: {self.base_url}")
        print("=" * 80)
        print()

        self.test_root_endpoint()
        self.test_hello_endpoint()
        self.test_hello_name_endpoint()
        self.test_mortgage_payment_endpoint()
        self.test_mortgage_breakdown_endpoint()

        print("✅ All API tests completed!")
        print("\n📝 Note: Update API_BASE_URL with your actual API Gateway URL after deployment")


def main():
    """Main function to run API examples"""
    print("📚 API Examples for Multi-Lambda Hello & Mortgage Service")
    print("=" * 80)
    print()

    # Check if requests library is available
    try:
        import requests
    except ImportError:
        print("❌ Error: requests library not found")
        print("Install it with: pip install requests")
        return

    # Create tester instance
    tester = APITester()

    print("Choose an option:")
    print("1. Test all endpoints")
    print("2. Test root endpoint only")
    print("3. Test hello endpoints")
    print("4. Test mortgage endpoints")
    print("5. Show curl examples")

    try:
        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            tester.run_all_tests()
        elif choice == "2":
            tester.test_root_endpoint()
        elif choice == "3":
            tester.test_hello_endpoint()
            tester.test_hello_name_endpoint()
        elif choice == "4":
            tester.test_mortgage_payment_endpoint()
            tester.test_mortgage_breakdown_endpoint()
        elif choice == "5":
            show_curl_examples()
        else:
            print("Invalid choice. Running all tests...")
            tester.run_all_tests()

    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")


def show_curl_examples():
    """Show curl command examples for all endpoints"""
    print("📝 cURL Examples")
    print("=" * 50)
    print()

    base_url = API_BASE_URL

    print("# Root endpoint - API information")
    print(f"curl {base_url}/")
    print()

    print("# Hello endpoint - basic greeting")
    print(f'curl "{base_url}/hello"')
    print()

    print("# Hello endpoint - excited mood with quote")
    print(f'curl "{base_url}/hello?mood=excited&quote=true"')
    print()

    print("# Hello name endpoint - basic personalized greeting")
    print(f'curl "{base_url}/hello/Alice"')
    print()

    print("# Hello name endpoint - formal Spanish greeting")
    print(f'curl "{base_url}/hello/María?style=formal&lang=es"')
    print()

    print("# Mortgage payment calculation")
    print(f'''curl -X POST {base_url}/mortgage/payment \\
  -H "Content-Type: application/json" \\
  -d '{{
    "property_value": 300000,
    "down_payment": 60000,
    "loan_years": 30,
    "interest_rate": 3.5,
    "currency": "EUR"
  }}\'''')
    print()

    print("# Mortgage breakdown - single month")
    print(f'''curl -X POST {base_url}/mortgage/breakdown \\
  -H "Content-Type: application/json" \\
  -d '{{
    "property_value": 300000,
    "down_payment": 60000,
    "loan_years": 30,
    "interest_rate": 3.5,
    "month": 1,
    "currency": "EUR"
  }}\'''')
    print()

    print("# Mortgage breakdown - amortization schedule (12 months)")
    print(f'''curl -X POST {base_url}/mortgage/breakdown \\
  -H "Content-Type: application/json" \\
  -d '{{
    "property_value": 300000,
    "down_payment": 60000,
    "loan_years": 30,
    "interest_rate": 3.5,
    "max_months": 12,
    "currency": "EUR"
  }}\'''')
    print()


if __name__ == "__main__":
    main()

# Refactoring Tools Example

[![01. Comby replace prints](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/01_comby_replace_prints.yml/badge.svg)](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/01_comby_replace_prints.yml) [![02. ast-grep replace prints](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/02_ast_grep_replace_print.yml/badge.svg)](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/02_ast_grep_replace_print.yml) [![03. ast-grep replace prints to powertools logger](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/03_ast_grep_replace_print_to_powertools_logger.yml/badge.svg)](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/03_ast_grep_replace_print_to_powertools_logger.yml) [![04. grit refactor](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/04_grit_refactor.yml/badge.svg)](https://github.com/pepitoenpeligro/refactoring-tools-examples/actions/workflows/04_grit_refactor.yml)


This repo holds a complete AWS CDK project howcasing five separate Python Lambda functions, each handling different API endpoints with unique functionality. Includes greeting services and mortgage calculation services following Clean Code and Hexagonal Architecture principles.

## 🏗️ Architecture

- **5 Lambda Functions**: Each endpoint powered by its own specialized Lambda function
- **API Gateway**: REST API routing requests to appropriate Lambda functions
- **CloudWatch Logs**: Individual log streams for each function
- **CloudFormation**: Infrastructure as Code via AWS CDK
- **Clean Architecture**: Domain-driven design with hexagonal architecture for mortgage calculations

## 📁 Project Structure

```
refactoring-tools-examples/
├── lambda_functions/
│   ├── root/                   # Root endpoint (/) Lambda
│   │   ├── handler.py         # API information service
│   │   └── requirements.txt   # Dependencies
│   ├── hello/                 # Hello endpoint (/hello) Lambda
│   │   ├── handler.py         # Random greetings service
│   │   └── requirements.txt   # Dependencies
│   ├── hello_name/            # Personalized endpoint (/hello/{name}) Lambda
│   │   ├── handler.py         # Name analysis & custom greetings
│   │   └── requirements.txt   # Dependencies
│   ├── mortgage_payment/      # Mortgage payment calculation Lambda
│   │   ├── handler.py         # Infrastructure layer (Lambda adapter)
│   │   ├── domain.py          # Domain entities and value objects
│   │   ├── service.py         # Application layer services
│   │   └── requirements.txt   # Dependencies
│   └── mortgage_breakdown/    # Mortgage breakdown calculation Lambda
│       ├── handler.py         # Infrastructure layer (Lambda adapter)
│       ├── domain.py          # Domain entities and value objects
│       ├── service.py         # Application layer services
│       └── requirements.txt   # Dependencies
├── stacks/
│   └── refactoring_tools_examples_stack.py  # CDK stack with 5 Lambdas
├── deploy.sh                  # Automated deployment script
├── test_lambda.py            # Comprehensive test suite
├── app.py                    # CDK app entry point
├── requirements.txt          # CDK dependencies
└── README.md                 # This file
```

## 🚀 Lambda Functions Overview

### 1. Root Lambda (`/`)
**Purpose**: API information and health check
- Provides service metadata and available endpoints
- Returns API version, status, and documentation
- Includes timestamp and environment information

**Features**:
- Service discovery endpoint
- API documentation generation
- Health status monitoring

### 2. Hello Lambda (`/hello`)
**Purpose**: Dynamic random greetings with motivational content
- Generates random greetings from a curated list
- Provides daily motivational quotes
- Supports mood-based greeting styles

**Features**:
- 8 different random greetings
- 8 motivational quotes
- Mood parameters: `happy`, `excited`, `calm`
- Optional quote inclusion via `?quote=true/false`

**Query Parameters**:
- `mood`: `happy|excited|calm` - Adjusts greeting style
- `quote`: `true|false` - Include/exclude motivational quote

### 3. Hello Name Lambda (`/hello/{name}`)
**Purpose**: Personalized greetings with name analysis
- Advanced name analysis (vowels, consonants, signatures)
- Multi-language support
- Various greeting styles
- Fun facts generation

**Features**:
- Name length and character analysis
- Lucky number generation based on name
- 4 greeting styles: `formal`, `casual`, `enthusiastic`, `poetic`
- 6 language options: `en`, `es`, `fr`, `de`, `it`, `pt`
- Personalized fun facts

**Query Parameters**:
- `style`: `formal|casual|enthusiastic|poetic` - Greeting style
- `lang`: `en|es|fr|de|it|pt` - Language preference

### 4. Mortgage Payment Lambda (`POST /mortgage/payment`)
**Purpose**: Calculate monthly mortgage payments with complete cost analysis
- Uses standard mortgage payment formula
- Supports zero-interest loans
- Provides total interest and payment breakdowns
- Follows Clean Code and Hexagonal Architecture

**Features**:
- Precise decimal calculations for financial accuracy
- Domain-driven design with value objects
- Comprehensive mortgage validation
- LTV ratio calculations
- Total cost analysis including down payment

**Request Body**:
```json
{
  "property_value": 300000,
  "down_payment": 60000,
  "loan_years": 30,
  "interest_rate": 3.5,
  "currency": "EUR"
}
```

### 5. Mortgage Breakdown Lambda (`POST /mortgage/breakdown`)
**Purpose**: Detailed amortization schedules and monthly payment breakdowns
- Month-by-month payment analysis
- Principal vs interest breakdown
- Remaining balance calculations
- Flexible schedule generation

**Features**:
- Single month breakdown analysis
- Multi-month amortization schedules
- Principal/interest percentage calculations
- Remaining balance tracking
- Schedule summary statistics

**Request Body Options**:
```json
// Single month breakdown
{
  "property_value": 300000,
  "down_payment": 60000,
  "loan_years": 30,
  "interest_rate": 3.5,
  "month": 1,
  "currency": "EUR"
}

// Amortization schedule
{
  "property_value": 250000,
  "down_payment": 50000,
  "loan_years": 25,
  "interest_rate": 4.0,
  "max_months": 12,
  "currency": "EUR"
}
```

## 🧪 API Endpoints

| Endpoint | Method | Lambda Function | Description | Example Response |
|----------|--------|----------------|-------------|-----------------|
| `/` | GET | Root Lambda | API information | Service metadata, endpoints list |
| `/hello` | GET | Hello Lambda | Random greeting | Random greeting + optional quote |
| `/hello/{name}` | GET | Hello Name Lambda | Personalized greeting | Custom greeting + name analysis |
| `/mortgage/payment` | POST | Mortgage Payment Lambda | Monthly payment calculation | Payment amount + total costs |
| `/mortgage/breakdown` | POST | Mortgage Breakdown Lambda | Amortization schedule | Monthly breakdowns + analysis |

### Example API Calls

```bash
# Root endpoint - API information
curl https://api-url/prod/

# Basic random greeting
curl https://api-url/prod/hello

# Excited mood greeting with quote
curl "https://api-url/prod/hello?mood=excited&quote=true"

# Basic personalized greeting
curl https://api-url/prod/hello/Alice

# Formal Spanish greeting
curl "https://api-url/prod/hello/Maria?style=formal&lang=es"

# Enthusiastic greeting
curl "https://api-url/prod/hello/Charlie?style=enthusiastic"

# Calculate monthly mortgage payment
curl -X POST https://api-url/prod/mortgage/payment \
  -H "Content-Type: application/json" \
  -d '{
    "property_value": 300000,
    "down_payment": 60000,
    "loan_years": 30,
    "interest_rate": 3.5,
    "currency": "EUR"
  }'

# Get single month breakdown
curl -X POST https://api-url/prod/mortgage/breakdown \
  -H "Content-Type: application/json" \
  -d '{
    "property_value": 300000,
    "down_payment": 60000,
    "loan_years": 30,
    "interest_rate": 3.5,
    "month": 1,
    "currency": "EUR"
  }'

# Get amortization schedule (first year)
curl -X POST https://api-url/prod/mortgage/breakdown \
  -H "Content-Type: application/json" \
  -d '{
    "property_value": 300000,
    "down_payment": 60000,
    "loan_years": 30,
    "interest_rate": 3.5,
    "max_months": 12,
    "currency": "EUR"
  }'

# Or use the interactive testing script
python3 api_examples.py
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js and npm
- AWS CLI configured with credentials
- AWS CDK CLI (`npm install -g aws-cdk`)

### Deploy

  ```bash
  # Setup virtual environment
  # uv v
  python3 -m venv .venv
  source .venv/bin/activate

  # Install dependencies
  # pip install -r requirements.txt
  pip install -r requirements.txt

  # Bootstrap CDK (first time only)
  # cdk bootstrap

  # Deploy stack
  cdk deploy --all -vv
  ```

3. **Test the deployed APIs**:
   ```bash
   # Interactive testing
   python3 api_examples.py

   # Or get API URL and test manually
   # The API URL will be in the CDK outputs
   ```

### Local Testing

Test all Lambda functions locally before deployment:

```bash
python3 test_lambda.py
```

This runs comprehensive tests for:
- ✅ Root Lambda functionality
- ✅ Hello Lambda with different moods
- ✅ Hello Name Lambda with various styles and languages
- ✅ Mortgage Payment Lambda with various scenarios
- ✅ Mortgage Breakdown Lambda with schedules and single months
- ✅ Error handling for all functions

### Integration Testing (After Deployment)

Test the deployed API Gateway and Lambda integration:

```bash
# CDK integration tests (automated deployment + testing)
cd integ-tests
cdk integ integ.api-gateway-lambda.py

# HTTP-based integration tests (against deployed API)
python integ-tests/run_integration_tests.py

# Or specify API URL manually
python integ-tests/run_integration_tests.py https://your-api-url
```

Integration tests validate:
- ✅ API Gateway routing to correct Lambda functions
- ✅ End-to-end request/response cycles
- ✅ CORS configuration and OPTIONS handling
- ✅ Error scenarios in deployed environment
- ✅ Performance metrics and response times

### Manual API Testing (After Deployment)

Use the interactive API testing script:

```bash
python3 api_examples.py
```

Choose from options:
1. Test all endpoints
2. Test root endpoint only
3. Test hello endpoints
4. Test mortgage endpoints
5. Show curl examples

## 📋 Response Examples

### Root Endpoint Response
```json
{
  "service": "Hello World API",
  "version": "1.0.0",
  "description": "A simple greeting service with multiple endpoints",
  "timestamp": "2025-01-15T10:30:00Z",
  "endpoints": [
    {"path": "/", "method": "GET", "description": "API information"},
    {"path": "/hello", "method": "GET", "description": "Simple greeting"},
    {"path": "/hello/{name}", "method": "GET", "description": "Personalized greeting"}
  ],
  "status": "healthy"
}
```

### Hello Endpoint Response
```json
{
  "greeting": "HOWDY, PARTNER! 🎉",
  "timestamp": "request-id-12345",
  "function": "hello-endpoint",
  "mood": "excited",
  "daily_motivation": "You are capable of amazing things."
}
```

### Hello Name Endpoint Response
```json
{
  "greeting": "¡Hola Maria! ¿Cómo estás?",
  "name_analysis": {
    "name": "Maria",
    "length": 5,
    "vowel_count": 3,
    "consonant_count": 2,
    "name_signature": "a1b2c3d4",
    "lucky_number": 42
  },
  "fun_facts": [
    "Your name has more vowels than consonants - that's melodic!"
  ],
  "processing_info": {
    "style": "casual",
    "language": "es",
    "timestamp": 1705320600
  }
}
```

### Mortgage Payment Response
```json
{
  "calculation_type": "monthly_payment",
  "input_parameters": {
    "property_value": {"amount": "300000.00", "currency": "EUR"},
    "loan_amount": {"amount": "240000.00", "currency": "EUR"},
    "loan_term_years": 30,
    "annual_interest_rate": "3.50",
    "loan_to_value_ratio": "80.00"
  },
  "results": {
    "monthly_payment": {"amount": "1077.71", "currency": "EUR"},
    "total_interest": {"amount": "147975.60", "currency": "EUR"},
    "total_amount_paid": {"amount": "387975.60", "currency": "EUR"},
    "total_cost_including_down_payment": {"amount": "447975.60", "currency": "EUR"},
    "interest_percentage_of_loan": "61.66"
  },
  "summary": {
    "description": "Monthly payment of 1077.71 EUR for 30 years (360 months)",
    "total_interest_cost": "147975.60 EUR",
    "effective_interest_rate": "61.66% of loan amount"
  }
}
```

### Mortgage Breakdown Response (Single Month)
```json
{
  "calculation_type": "single_month_breakdown",
  "month_breakdown": {
    "month_number": 1,
    "total_payment": {"amount": "1077.71", "currency": "EUR"},
    "principal_payment": {
      "amount": "377.71",
      "currency": "EUR",
      "percentage": "35.03"
    },
    "interest_payment": {
      "amount": "700.00",
      "currency": "EUR",
      "percentage": "64.97"
    },
    "remaining_balance": {"amount": "239622.29", "currency": "EUR"}
  },
  "summary": {
    "description": "Payment breakdown for month 1",
    "principal_vs_interest": "35.0% principal, 65.0% interest",
    "remaining_balance": "239622.29 EUR remaining after this payment"
  }
}
```

## 🔧 Development

### Adding New Lambda Functions

1. Create new directory under `lambda_functions/`
2. Add `handler.py` with your function code
3. Create `requirements.txt` for dependencies
4. Update CDK stack to include the new function
5. Add routes in API Gateway configuration

### Lambda Function Template

```python
import json
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function description.
    """
    try:
        print("Function called - processing request")

        # Your logic here

        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Success'
            })
        }

        print("Response generated successfully")
        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
```

### Mortgage Domain Architecture

The mortgage calculation functions follow Clean Code and Hexagonal Architecture:

```python
# Domain Layer - Pure business logic
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "EUR"

@dataclass(frozen=True)
class MortgageRequest:
    property_value: Money
    down_payment: Money
    loan_term: LoanTerm
    interest_rate: InterestRate

# Application Layer - Use cases
class MortgageCalculatorService:
    def calculate_monthly_payment(self, request: MortgageRequest) -> Money:
        # Business logic implementation

# Infrastructure Layer - Adapters
def lambda_handler(event, context):
    # Convert event to domain objects
    # Execute business logic
    # Convert result to response
```

### Environment Variables

Each Lambda function can be configured with environment variables in the CDK stack:

```python
environment={
    "LOG_LEVEL": "INFO",
    "ENVIRONMENT": "dev",
    "ENDPOINT": "function_name"
}
```

## 🛠️ CDK Commands

```bash
cdk ls          # List all stacks
cdk synth       # Synthesize CloudFormation template
cdk deploy      # Deploy stack
cdk destroy     # Remove stack
cdk diff        # Compare deployed stack with current state
```

## 🧹 Cleanup

To remove all AWS resources:

```bash
cdk destroy
```

## 🔍 Monitoring

### CloudWatch Logs
Each Lambda function has its own log group:
- `/aws/lambda/RefactoringToolsExamplesStack-RootFunction`
- `/aws/lambda/RefactoringToolsExamplesStack-HelloFunction`
- `/aws/lambda/RefactoringToolsExamplesStack-HelloNameFunction`
- `/aws/lambda/RefactoringToolsExamplesStack-MortgagePaymentFunction`
- `/aws/lambda/RefactoringToolsExamplesStack-MortgageBreakdownFunction`

### CloudWatch Metrics
Monitor function performance:
- Duration, Invocations, Errors, Throttles
- Memory utilization, Cold starts
- API Gateway request/response metrics


## 🧪 Testing Strategy

### 1. Local Testing (Development)
Test all Lambda functions locally before deployment:

```bash
python3 test_lambda.py
```

### 2. Integration Testing (Deployed Environment)
Test API Gateway and Lambda integration in real AWS environment:

```bash
# CDK integration tests (recommended)
cd integ-tests
cdk integ integ.api-gateway-lambda.py

# HTTP-based integration tests
python integ-tests/run_integration_tests.py
```

### 3. Manual API Testing
Interactive testing of deployed APIs:

```bash
python3 api_examples.py
```

### 4. Manual Endpoint Testing
Direct testing with curl:

```bash
# Get API URL from CDK outputs
cdk ls --long

# Test endpoints manually
curl https://your-api-id.execute-api.region.amazonaws.com/prod/
```



## 📄 License

This project is provided as an example for educational purposes under MIT license.

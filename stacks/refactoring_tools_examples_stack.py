from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_logs as logs,
    CfnOutput,
)
from constructs import Construct
import os


class RefactoringToolsExamplesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Root Lambda function (for / endpoint)
        root_lambda = _lambda.Function(
            self, "RootFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "..", "lambda_functions", "root")
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "dev",
                "ENDPOINT": "root"
            },
            description="Root API endpoint Lambda function - provides API information",
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Hello Lambda function (for /hello endpoint)
        hello_lambda = _lambda.Function(
            self, "HelloFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "..", "lambda_functions", "hello")
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "dev",
                "ENDPOINT": "hello"
            },
            description="Hello endpoint Lambda function - provides random greetings",
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Hello Name Lambda function (for /hello/{name} endpoint)
        hello_name_lambda = _lambda.Function(
            self, "HelloNameFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "..", "lambda_functions", "hello_name")
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "dev",
                "ENDPOINT": "hello_name"
            },
            description="Personalized hello endpoint Lambda function - provides customized greetings",
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Mortgage Payment Lambda function (for /mortgage/payment endpoint)
        mortgage_payment_lambda = _lambda.Function(
            self, "MortgagePaymentFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "..", "lambda_functions", "mortgage_payment")
            ),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "dev",
                "ENDPOINT": "mortgage_payment"
            },
            description="Mortgage payment calculator following Clean Code and Hexagonal Architecture",
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Mortgage Breakdown Lambda function (for /mortgage/breakdown endpoint)
        mortgage_breakdown_lambda = _lambda.Function(
            self, "MortgageBreakdownFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "..", "lambda_functions", "mortgage_breakdown")
            ),
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "dev",
                "ENDPOINT": "mortgage_breakdown"
            },
            description="Mortgage amortization schedule calculator with detailed breakdowns",
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # API Gateway
        api = apigateway.RestApi(
            self, "MultiLambdaApi",
            rest_api_name="Multi-Lambda Hello & Mortgage Service",
            description="API Gateway with separate Lambda functions for greetings and mortgage calculations",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Requested-With"]
            ),
            cloud_watch_role=True,
        )

        # Lambda integrations
        root_integration = apigateway.LambdaIntegration(
            root_lambda,
            request_templates={
                "application/json": '{ "statusCode": "200" }'
            }
        )

        hello_integration = apigateway.LambdaIntegration(
            hello_lambda,
            request_templates={
                "application/json": '{ "statusCode": "200" }'
            }
        )

        hello_name_integration = apigateway.LambdaIntegration(
            hello_name_lambda,
            request_templates={
                "application/json": '{ "statusCode": "200" }'
            }
        )

        mortgage_payment_integration = apigateway.LambdaIntegration(
            mortgage_payment_lambda,
            request_templates={
                "application/json": '{ "statusCode": "200" }'
            }
        )

        mortgage_breakdown_integration = apigateway.LambdaIntegration(
            mortgage_breakdown_lambda,
            request_templates={
                "application/json": '{ "statusCode": "200" }'
            }
        )

        # Root endpoint: GET / -> root_lambda
        api.root.add_method("GET", root_integration)

        # Hello endpoint: GET /hello -> hello_lambda
        hello_resource = api.root.add_resource("hello")
        hello_resource.add_method("GET", hello_integration)

        # Dynamic endpoint: GET /hello/{name} -> hello_name_lambda
        name_resource = hello_resource.add_resource("{name}")
        name_resource.add_method("GET", hello_name_integration)

        # Mortgage endpoints: POST /mortgage/payment and POST /mortgage/breakdown
        mortgage_resource = api.root.add_resource("mortgage")

        # Payment endpoint: POST /mortgage/payment -> mortgage_payment_lambda
        payment_resource = mortgage_resource.add_resource("payment")
        payment_resource.add_method("POST", mortgage_payment_integration)

        # Breakdown endpoint: POST /mortgage/breakdown -> mortgage_breakdown_lambda
        breakdown_resource = mortgage_resource.add_resource("breakdown")
        breakdown_resource.add_method("POST", mortgage_breakdown_integration)

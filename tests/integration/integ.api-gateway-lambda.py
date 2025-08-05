#!/usr/bin/env python3

"""
Integration test for API Gateway and Lambda functions.
This test follows the CDK integration test pattern.
"""

import os
import sys
import aws_cdk as cdk
from aws_cdk import integ_tests_alpha as integ

# Add the project root to the Python path so we can import our stack
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from stacks.refactoring_tools_examples_stack import RefactoringToolsExamplesStack

# Create the CDK app
app = cdk.App()

# Create the test stack
test_stack = RefactoringToolsExamplesStack(
    app, "IntegTestApiGatewayLambdaStack",
    description="Integration test stack for API Gateway and Lambda functions"
)

# Create the integration test
integration_test = integ.IntegTest(
    app, "ApiGatewayLambdaIntegrationTest",
    test_cases=[test_stack]
)

app.synth()

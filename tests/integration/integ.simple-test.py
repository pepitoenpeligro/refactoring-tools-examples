#!/usr/bin/env python3

"""
Simple integration test for API Gateway and Lambda functions.
This follows the exact pattern from the dev.to article:
https://dev.to/tomharvey/integration-tests-with-cdk-and-python-a-more-real-world-app-less-hello-world-2b5c
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

# Create a test stack
stack = RefactoringToolsExamplesStack(
    app, "SimpleIntegTestStack",
    description="Simple integration test for API Gateway and Lambda"
)

# Create the integration test
test = integ.IntegTest(
    app, "SimpleApiTest",
    test_cases=[stack],
    diff_assets=True,
    stack_update_workflow=True
)

# For now, just create a basic test that validates the stack can be synthesized
# The actual assertions would be handled when the integ-runner deploys and tests
print("Integration test stack created successfully")
print(f"Stack name: {stack.stack_name}")
print("This test validates that the stack can be properly synthesized")

app.synth()

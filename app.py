#!/usr/bin/env python3
import os

import aws_cdk as cdk

from .stacks.refactoring_tools_examples_stack import RefactoringToolsExamplesStack


app = cdk.App()
RefactoringToolsExamplesStack(app, "RefactoringToolsExamplesStack",
  env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()

import aws_cdk as core
import aws_cdk.assertions as assertions

from refactoring_tools_examples.refactoring_tools_examples_stack import RefactoringToolsExamplesStack

def test_sqs_queue_created():
    app = core.App()
    stack = RefactoringToolsExamplesStack(app, "refactoring-tools-examples")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

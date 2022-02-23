import aws_cdk as core
import aws_cdk.assertions as assertions

from codedeploy_ec2_bg.codedeploy_ec2_bg_stack import CodedeployEc2BgStack

# example tests. To run these tests, uncomment this file along with the example
# resource in codedeploy_ec2_bg/codedeploy_ec2_bg_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CodedeployEc2BgStack(app, "codedeploy-ec2-bg")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

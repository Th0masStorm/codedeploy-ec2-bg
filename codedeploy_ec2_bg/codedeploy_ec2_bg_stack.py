from email import policy
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_codecommit as cc,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codedeploy as cd,
    aws_codepipeline_actions as cp_actions,
)
from constructs import Construct

class CodedeployEc2BgStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc =  ec2.Vpc(self, "vpc", max_azs=2)

        user_data_file = open('files/user-data', 'rb').read()
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(str(user_data_file, 'utf-8'))
        instance_type = ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO)
        ami = ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2)

        asg_iam_role = iam.Role(self, 'role', assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'))
        asg_iam_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonEC2RoleforAWSCodeDeploy'))
        asg_iam_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'))

        asg1 = autoscaling.AutoScalingGroup(
            self,"asg1", vpc=vpc,
            instance_type=instance_type,
            machine_image=ami,
            role=asg_iam_role,
            user_data=user_data
            )

        alb = elbv2.ApplicationLoadBalancer(
            self, "alb",
            vpc=vpc,
            internet_facing=True)

        repo = cc.Repository(self, 'repo', code=cc.Code.from_directory('src/'), repository_name='repo')
        build = cb.PipelineProject(self, 'build')
        app = cd.ServerApplication(self, 'app', application_name='app')
        dgroup = cd.ServerDeploymentGroup(self, 'dgroup', auto_scaling_groups=[asg1], application=app)
        source_out = cp.Artifact()
        build_out = cp.Artifact()

        source_action = cp_actions.CodeCommitSourceAction(
            action_name='CodeCommit',
            repository=repo,
            output=source_out
        )

        build_action = cp_actions.CodeBuildAction(
            action_name='CodeBuild',
            project=build,
            input=source_out,
            outputs=[build_out],
        )

        deploy_action = cp_actions.CodeDeployServerDeployAction(
            action_name='Deploy',
            deployment_group=dgroup,
            input=build_out
        )


        cp.Pipeline(self, 'pipeline',
        stages=[
            cp.StageProps(stage_name='Source',actions=[source_action]),
            cp.StageProps(stage_name='Build', actions=[build_action]),
            cp.StageProps(stage_name='Deploy', actions=[deploy_action])
        ])


        listener = alb.add_listener("Listener", port=80)
        listener.add_targets("Target", port=8080, targets=[asg1])
        listener.connections.allow_default_port_from_any_ipv4("Open to the world")

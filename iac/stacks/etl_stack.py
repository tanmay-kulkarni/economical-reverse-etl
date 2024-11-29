from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    Duration,
)
from constructs import Construct

class EtlStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # Create VPC
        vpc = ec2.Vpc(self, f"{env_name}-vpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='Private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )
        
        # Create S3 bucket for ETL code
        etl_bucket = s3.Bucket(self, f"{env_name}-etl-bucket")
        
        # Create SNS topic for ETL completion notifications using config
        completion_topic = sns.Topic(
            self, f"{env_name}-etl-completion-topic",
            topic_name=config['sns']['topic_name']
        )
        
        # Create IAM role for EC2 instances
        ec2_role = iam.Role(
            self, f"{env_name}-ec2-role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        
        # Add permissions to EC2 role
        ec2_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonS3ReadOnlyAccess"
            )
        )
        
        # Add SNS publish permissions to EC2 role
        ec2_role.add_to_policy(
            iam.PolicyStatement(
                actions=["sns:Publish"],
                resources=[completion_topic.topic_arn]
            )
        )
        
        # Create instance profile
        instance_profile = iam.CfnInstanceProfile(
            self, f"{env_name}-instance-profile",
            roles=[ec2_role.role_name]
        )
        
        # Create security group for EC2
        security_group = ec2.SecurityGroup(
            self, f"{env_name}-sg",
            vpc=vpc,
            description="Security group for ETL instances",
            allow_all_outbound=True
        )
        
        # Create trigger Lambda function
        trigger_lambda = lambda_.Function(
            self, f"{env_name}-trigger-etl",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("../src/lambda/trigger_etl"),
            environment={
                "SUBNET_ID": vpc.private_subnets[0].subnet_id,
                "SECURITY_GROUP_ID": security_group.security_group_id,
                "INSTANCE_PROFILE": instance_profile.ref,
                "ETL_BUCKET": etl_bucket.bucket_name,
                "COMPLETION_TOPIC_ARN": completion_topic.topic_arn,
                "ENVIRONMENT": env_name
            },
            timeout=Duration.minutes(5)
        )
        
        # Grant trigger Lambda permissions to launch EC2 instances
        trigger_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ec2:RequestSpotInstances",
                    "ec2:DescribeSpotInstanceRequests",
                    "iam:PassRole"
                ],
                resources=["*"]
            )
        )
        
        # Create cleanup Lambda function
        cleanup_lambda = lambda_.Function(
            self, f"{env_name}-cleanup-spot",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("../src/lambda/cleanup_spot"),
            environment={
                "ENVIRONMENT": env_name
            },
            timeout=Duration.minutes(5)
        )
        
        # Grant cleanup Lambda permission to terminate EC2 instances
        cleanup_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ec2:TerminateInstances"],
                resources=["*"]
            )
        )
        
        # Subscribe cleanup Lambda to the SNS topic
        completion_topic.add_subscription(
            sns_subscriptions.LambdaSubscription(cleanup_lambda)
        )
        
        # Create EventBridge rule to trigger ETL
        rule = events.Rule(
            self, f"{env_name}-schedule",
            schedule=events.Schedule.rate(Duration.hours(1))
        )
        rule.add_target(targets.LambdaFunction(trigger_lambda))
        
        # Grant bucket permissions
        etl_bucket.grant_read(trigger_lambda)
        
        # Add environment-specific tags
        self.tags.set_tag('Environment', env_name)
        self.tags.set_tag('Project', 'reverse-etl')
        
        # Output important values
        self.etl_bucket_name = etl_bucket.bucket_name
        self.completion_topic_arn = completion_topic.topic_arn
        self.vpc_id = vpc.vpc_id

    @property
    def outputs(self):
        return {
            'etlBucketName': self.etl_bucket_name,
            'completionTopicArn': self.completion_topic_arn,
            'vpcId': self.vpc_id
        }
import json
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_events as events,
)
from constructs import Construct

class EtlStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create S3 bucket
        bucket = s3.Bucket(self, f"{env_name}-etl-bucket")

        # Use config for EC2 instance type
        vpc = ec2.Vpc(self, f"{env_name}-vpc")
        instance = ec2.SpotInstance(self, f"{env_name}-spot",
            instance_type=ec2.InstanceType(config['spot_instance']['instance_type']),
            vpc=vpc
        )

        # Create Lambda function with environment variables from config
        lambda_fn = lambda_.Function(self, f"{env_name}-transformer",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("../src/lambda"),
            environment={
                "REDSHIFT_CLUSTER": config['redshift']['cluster'],
                "REDSHIFT_DATABASE": config['redshift']['database'],
                "POSTGRES_HOST": config['postgres']['host'],
                "POSTGRES_DATABASE": config['postgres']['database']
            }
        )
import boto3
import os
import base64

def get_user_data_script():
    """
    Creates a user data script that will be executed when the EC2 instance starts.
    This script sets up the environment and runs the ETL process.
    """
    env_name = os.environ['ENVIRONMENT']
    return f"""#!/bin/bash
# Install dependencies
yum update -y
yum install -y python3-pip git

# Set environment variables
echo "export COMPLETION_TOPIC_ARN={os.environ['COMPLETION_TOPIC_ARN']}" >> /etc/environment
echo "export ENVIRONMENT={env_name}" >> /etc/environment
source /etc/environment

# Create directory for ETL
mkdir -p /opt/etl

# Get ETL code
aws s3 cp s3://{os.environ['ETL_BUCKET']}/etl.zip /opt/etl/
cd /opt/etl
unzip etl.zip

# Install Python requirements
pip3 install -r requirements.txt

# Run the ETL process
python3 main.py
"""

def handler(event, context):
    """Lambda function to launch EC2 spot instance and run ETL"""
    try:
        ec2 = boto3.client('ec2')
        
        # Get configuration from environment variables
        subnet_id = os.environ['SUBNET_ID']
        security_group_id = os.environ['SECURITY_GROUP_ID']
        instance_profile = os.environ['INSTANCE_PROFILE']
        
        # Launch spot instance
        response = ec2.request_spot_instances(
            InstanceCount=1,
            LaunchSpecification={
                'ImageId': 'ami-0123456789',  # Replace with valid Amazon Linux 2 AMI ID
                'InstanceType': 't3.micro',
                'SubnetId': subnet_id,
                'SecurityGroupIds': [security_group_id],
                'IamInstanceProfile': {
                    'Name': instance_profile
                },
                'UserData': base64.b64encode(
                    get_user_data_script().encode()
                ).decode('utf-8')
            },
            Type='one-time'
        )
        
        spot_request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
        
        print(f"Launched spot instance request: {spot_request_id}")
        
        return {
            'statusCode': 200,
            'body': {
                'spotRequestId': spot_request_id
            }
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }
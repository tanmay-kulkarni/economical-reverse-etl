import boto3
import json

def handler(event, context):
    """Lambda function to terminate spot instance"""
    try:
        # Parse the SNS message
        message = json.loads(event['Records'][0]['Sns']['Message'])
        instance_id = message['instance_id']
        
        # Terminate the instance
        ec2 = boto3.client('ec2')
        ec2.terminate_instances(InstanceIds=[instance_id])
        
        print(f"Successfully terminated instance: {instance_id}")
        return {
            'statusCode': 200,
            'body': f"Terminated instance {instance_id}"
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }
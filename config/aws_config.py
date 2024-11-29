import boto3
from typing import Dict
import os

class AWSConfig:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name='us-east-1'):
        """
        Initialize AWS configuration with credentials and multiple services
        
        Args:
            aws_access_key_id (str): AWS access key
            aws_secret_access_key (str): AWS secret access key
            region_name (str): AWS region name (default: 'us-east-1')
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        
        # Initialize all clients to None
        self.s3_client = None
        self.rekognition_client = None
        self.bedrock_runtime_client = None
    
    def get_client(self) -> Dict:
        return {
            's3': boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            ),
            'rekognition': boto3.client(
                'rekognition',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            ),
            'bedrock':  boto3.client(
                'bedrock-runtime',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
        }
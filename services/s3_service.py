from typing import Optional
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    def read_image(self, bucket: str, key: str) -> bytes: 
        """Read image from S3 bucket""" 
        try:  
            response = self.s3_client.get_object(Bucket=bucket, Key=key) 
            return response['Body'].read() 
        except Exception as e:
            logger.error(f"Error reading from S3: {e}") 
            raise
    
    def upload_file(self, file_name: str, bucket: str, object_name: Optional[str] = None) -> bool:
        if object_name is None:
            object_name = file_name
        try:
            self.s3_client.upload_file(file_name, bucket, object_name)
            logger.info(f"File {file_name} uploaded to {bucket}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"Error uploading file {file_name} to {bucket}/{object_name}: {e}")
            return False

    def upload_text(self, bucket: str, key: str, text_content: str) -> bool:
        """Upload text content to S3"""
        try:
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=text_content.encode('utf-8'),
                ContentType='text/plain'
            )
            logger.info(f"Successfully uploaded text content to {bucket}/{key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading text content to {bucket}/{key}: {e}")
            return False
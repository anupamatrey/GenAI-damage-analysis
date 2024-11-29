import boto3
from typing import Optional, Dict, List
from datetime import datetime
import logging
from services.s3_service import S3Service
from services.rekognition_service import RekognitionService
from services.bedrock_service import BedrockService

logger = logging.getLogger(__name__)

class MultiImageDamageAnalyzer:
    def __init__(self, s3_service: S3Service, rekognition_service: RekognitionService, bedrock_service: BedrockService):
        """
        Initialize MultiImageDamageAnalyzer with required services
        """
        self.s3_service = s3_service
        self.rekognition_service = rekognition_service
        self.bedrock_service = bedrock_service
        self.s3_client = boto3.client('s3')

    def list_jpg_images(self, source_bucket: str) -> List[str]:
        """
        List all JPG/JPEG images in the source bucket
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=source_bucket)
            return [
                obj['Key'] for obj in response.get('Contents', []) 
                if obj['Key'].lower().endswith(('.jpg', '.jpeg'))
            ]
        except Exception as e:
            logger.error(f"Error listing images: {e}")
            return []

    def process_images(self, source_bucket: str, output_bucket: Optional[str] = None) -> List[Dict]:
        """
        Process all images in the source bucket
        """
        image_keys = self.list_jpg_images(source_bucket)
        
        if not image_keys:
            logger.warning("No images found in the source bucket")
            return []
        
        processing_results = []

        for source_key in image_keys:
            try:
                # Read image bytes
                image_bytes = self.s3_service.read_image(source_bucket, source_key)
               
                # Detect damage from S3 reference
                s3_reference = {'Bucket': source_bucket, 'Name': source_key}
                damage_labels = self.rekognition_service.detect_damage(
                    s3_reference,
                    source_type='s3'
                )
               
                # Generate report using image bytes
                report = self.bedrock_service.generate_report(
                    image_bytes, damage_labels
                )
               
                # Save report if output bucket specified
                if output_bucket:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    report_key = f"reports/{source_key.split('/')[-1]}_{timestamp}.txt"
                    upload_success = self.s3_service.upload_text(
                        bucket=output_bucket,
                        key=report_key,
                        text_content=report
                    )
                    if not upload_success:
                        logger.warning(f"Failed to save report for {source_key}")
               
                processing_results.append({
                    'source_key': source_key,
                    'damage_labels': damage_labels,
                    'report': report
                })
               
            except Exception as e:
                logger.error(f"Error processing {source_key}: {e}")
                continue
        
        return processing_results
from typing import Optional, Dict, List
from datetime import datetime
import logging
from services.s3_service import S3Service
from services.rekognition_service import RekognitionService
from services.bedrock_service import BedrockService

logger = logging.getLogger(__name__)

class DamageAnalyzer:
    def __init__(self, s3_service: S3Service, rekognition_service: RekognitionService, bedrock_service: BedrockService):
        """
        Initialize DamageAnalyzer with required services
        """
        self.s3_service = s3_service
        self.rekognition_service = rekognition_service
        self.bedrock_service = bedrock_service

    def analyze_damage(self, source_bucket: str, source_key: str, output_bucket: Optional[str] = None) -> Dict:
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
            #if output_bucket:
             #   timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
              #  report_key = f"reports/{source_key.split('/')[-1]}_{timestamp}.txt"
               # self.s3_service.upload_file(output_bucket, report_key, report)

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
                    logger.warning("Failed to save report to S3")
            
            return {
                'damage_labels': damage_labels,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise
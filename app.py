import logging
from config.aws_config import AWSConfig
from services.s3_service import S3Service
from services.rekognition_service import RekognitionService
from services.bedrock_service import BedrockService
from analyzers.damage_analyzer import DamageAnalyzer
from analyzers.multiimagedamage_analyzer import MultiImageDamageAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize AWS configuration
        aws_config = AWSConfig(
            region_name='us-east-1'
        )
        aws_clients = aws_config.get_client()
        
        # Initialize services
        s3_service = S3Service(aws_clients['s3'])
        rekognition_service = RekognitionService(aws_clients['rekognition'])
        bedrock_service = BedrockService(aws_clients['bedrock'])
        
        # Initialize analyzer with services
        analyzer = MultiImageDamageAnalyzer(
            s3_service=s3_service,
            rekognition_service=rekognition_service,
            bedrock_service=bedrock_service
        )
        
        # Configuration
        source_bucket = 'damage-analyzer1124-test'
        #source_key = 'damage_images/home.jpg'
        output_bucket = 'damage-analyzer1124-test'  # Optional
        
        # Perform analysis
        #result = analyzer.analyze_damage(
        results = analyzer.process_images(
            source_bucket=source_bucket,
            #source_key=source_key,
            output_bucket=output_bucket
        )
        
        # Log results
        for result in results:
            print(f"Image: {result['source_key']}")
            print("Damage Labels:", result['damage_labels'])
            print("Report:", result['report'])
            print("-" * 50)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()
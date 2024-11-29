# services/bedrock_service.py
import json 
import base64 
import logging 
from typing import Dict 
logger = logging.getLogger(__name__) 

class BedrockService: 
    def __init__(self, bedrock_client):  
        self.client = bedrock_client
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    def generate_report(self, image_bytes: bytes, damage_labels: list[Dict]) -> str: 
        """Generate analysis report using Bedrock""" 
        try:  
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            prompt = f"""Analyze the following image for damage.  Detected potential damage indicators: {json.dumps(damage_labels)}  
            Provide a detailed damage assessment including:  
            1. Type and extent of damage  
            2. Estimated repair complexity  
            3. Potential repair cost range  
            4. Recommendations for next steps  Be specific and use the detected labels as context."""
            
            body = json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 300,
                    "temperature": 0.7,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": base64_image
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
            )

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json" 
            ) 
            return json.loads(response['body'].read())['content'][0]['text'] 
        except Exception as e:  
            logger.error(f"Bedrock error: {e}") 
            raise

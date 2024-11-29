from typing import List,Dict,Union 
import logging 
from datetime import datetime 
logger = logging.getLogger(__name__) 

class RekognitionService: 
    def __init__(self, rekognition_client):  
        self.client = rekognition_client  
        self.damage_keywords = [
                                    # Physical damage
                                    'damage', 'crack', 'scratch', 'dent', 'broken', 'chip', 'split', 'tear', 
                                    'puncture', 'gouge', 'rupture', 'fissure', 'fracture', 'destroyed',
                                    
                                    # Surface-specific damage
                                    'rust', 'corrosion', 'wear', 'deterioration', 'degradation', 'erosion', 
                                    'stain', 'discoloration', 'peeling', 'chipped paint', 'surface damage',
                                    
                                    # Structural damage
                                    'deformation', 'warped', 'bent', 'misaligned', 'collapsed', 'buckled', 
                                    'twisted', 'structural failure', 'compromised',
                                    
                                    # Material-specific damage
                                    'shattered', 'cracked glass', 'metal fatigue', 'material failure', 
                                    'structural weakness', 'fragmented',
                                    
                                    # Contextual damage indicators
                                    'impact', 'collision', 'accident', 'trauma', 'stress', 'strain', 
                                    'mechanical failure', 'structural compromise'
        ]

    def detect_damage(self, image: Union[Dict, bytes], source_type: str = 's3') -> List[Dict]: 
        """  Detect damage using Rekognition  :param image: Image source (S3 object reference or image bytes)  :param source_type: 's3' or 'bytes'  :return: List of damage-related labels  """ 
        try: # Prepare image reference based on source type 
            if source_type == 's3':  
                image_reference = {'S3Object': image} 
            elif source_type == 'bytes':  
                image_reference = {'Bytes': image} 
            else: 
                raise ValueError("Invalid source type. Use 's3' or 'bytes'.")  
            
            response = self.client.detect_labels(  
                Image=image_reference,  MaxLabels=10,  MinConfidence=70.0 
            ) 
            
            return [  
                label for label in response['Labels'] 
                if any(keyword in label['Name'].lower() for keyword in self.damage_keywords) 
            ] 
        except Exception as e:
            logger.error(f"Rekognition error: {e}") 
            raise
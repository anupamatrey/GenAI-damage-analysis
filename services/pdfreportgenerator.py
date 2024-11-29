import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import boto3

class PDFReportGenerator:
    def __init__(self, s3_client=None):
        """
        Initialize PDF Report Generator
        
        :param s3_client: Optional S3 client for report storage
        """
        self.s3_client = s3_client or boto3.client('s3')
        self.styles = getSampleStyleSheet()
    
    def generate_damage_report_pdf(self, 
                                    report_details: dict, 
                                    output_bucket: str = None) -> str:
        """
        Generate a PDF report from damage analysis details
        
        :param report_details: Dictionary containing damage report information
        :param output_bucket: Optional S3 bucket to store the PDF
        :return: PDF file key or local file path
        """
        # Create an in-memory PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Add title
        title = Paragraph(f"Damage Analysis Report: {report_details.get('moved_image_key', 'Unnamed Image')}", 
                          self.styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Add damage labels
        labels_text = "Damage Labels: " + ", ".join(report_details.get('damage_labels', ['No labels detected']))
        story.append(Paragraph(labels_text, self.styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Add detailed report
        report_content = report_details.get('report', 'No detailed report available')
        story.append(Paragraph(report_content, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Reset buffer position
        buffer.seek(0)
        
        # Optional S3 upload
        if output_bucket:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_key = f"reports/{report_details.get('moved_image_key', 'report')}_{timestamp}.pdf"
            
            self.s3_client.put_object(
                Bucket=output_bucket,
                Key=file_key,
                Body=buffer.getvalue()
            )
            return file_key
        
        return buffer
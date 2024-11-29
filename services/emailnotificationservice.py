import boto3
import logging
from typing import Dict, List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class EmailNotificationService:
    def __init__(self, ses_client=None):
        """
        Initialize SES client for sending emails
        
        :param ses_client: Optional pre-configured SES client
        """
        self.ses_client = ses_client or boto3.client('ses')
        self.logger = logging.getLogger(__name__)
    
    def _create_email_body(self, report_details: Dict) -> str:
        """
        Create HTML email body from report details
        
        :param report_details: Dictionary containing report information
        :return: HTML formatted email body
        """
        return f"""
        <html>
        <body>
            <h2>Damage Report</h2>
            <p><strong>Image:</strong> {report_details.get('moved_image_key', 'N/A')}</p>
            <p><strong>Damage Labels:</strong> {', '.join(report_details.get('damage_labels', []))}</p>
            <h3>Detailed Report</h3>
            <p>{report_details.get('report', 'No detailed report available')}</p>
        </body>
        </html>
        """
    
    def send_report_email(self, 
                           recipient: str, 
                           report_details: Dict, 
                           s3_client=None, 
                           processed_bucket: str = None) -> bool:
        """
        Send email with damage report and attached PDF
        
        :param recipient: Email address of recipient
        :param report_details: Dictionary containing report details
        :param s3_client: Optional S3 client for retrieving report
        :param processed_bucket: Bucket containing processed reports
        :return: Boolean indicating email sending success
        """
        s3_client = s3_client or boto3.client('s3')
        
        try:
            # Create multipart message
            msg = MIMEMultipart()
            msg['Subject'] = f"Damage Report for {report_details.get('moved_image_key')}"
            msg['From'] = "your-verified-email@example.com"  # Replace with verified SES email
            msg['To'] = recipient
            
            # Attach HTML body
            msg.attach(MIMEText(self._create_email_body(report_details), 'html'))
            
            # Attempt to attach PDF report if exists
            try:
                report_key = report_details.get('report_key')
                if report_key and processed_bucket:
                    report_obj = s3_client.get_object(Bucket=processed_bucket, Key=report_key)
                    report_content = report_obj['Body'].read()
                    
                    pdf_part = MIMEApplication(report_content, _subtype='pdf')
                    pdf_part.add_header('Content-Disposition', 'attachment', filename=report_key.split('/')[-1])
                    msg.attach(pdf_part)
            except Exception as pdf_error:
                self.logger.warning(f"Could not attach PDF: {pdf_error}")
            
            # Send email
            response = self.ses_client.send_raw_email(
                Source=msg['From'],
                Destinations=[recipient],
                RawMessage={'Data': msg.as_string()}
            )
            
            self.logger.info(f"Email sent successfully to {recipient}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
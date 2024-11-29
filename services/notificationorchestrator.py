class NotificationOrchestrator:
    def __init__(self, 
                 aws_config,
                 source_bucket: str, 
                 processed_bucket: str,
                 email_notification_service: EmailNotificationService = None):
        """
        Orchestrate image processing and notification workflow
        
        :param aws_config: AWS configuration object
        :param source_bucket: Source bucket for images
        :param processed_bucket: Processed bucket for reports
        :param email_notification_service: Optional email notification service
        """
        self.multi_image_analyzer = MultiImageDamageAnalyzer(aws_config)
        self.processed_bucket = processed_bucket
        
        # Use provided or create new email notification service
        self.email_service = email_notification_service or EmailNotificationService()
    
    def process_and_notify(self, 
                            customer_email: str, 
                            source_bucket: str = None) -> List[Dict]:
        """
        Process images and send notifications
        
        :param customer_email: Email address to send notifications
        :param source_bucket: Optional source bucket (uses class-level if not provided)
        :return: List of processing results
        """
        source_bucket = source_bucket or self.multi_image_analyzer.source_bucket
        
        # Process images
        results = self.multi_image_analyzer.process_images(
            source_bucket, 
            self.processed_bucket
        )
        
        # Send notifications for each processed image
        for result in results:
            self.email_service.send_report_email(
                recipient=customer_email, 
                report_details=result,
                processed_bucket=self.processed_bucket
            )
        
        return results
"""
S3 Service for PDF Storage
Handles uploading PDF files to AWS S3
"""
import boto3
import os
from typing import Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """Service for uploading files to AWS S3"""
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1"
    ):
        """
        Initialize S3 service
        
        Args:
            bucket_name: S3 bucket name (defaults to env var AWS_S3_BUCKET)
            aws_access_key_id: AWS access key (defaults to env var AWS_ACCESS_KEY_ID)
            aws_secret_access_key: AWS secret key (defaults to env var AWS_SECRET_ACCESS_KEY)
            region_name: AWS region (defaults to us-east-1)
        """
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET", "rightcarehome-reports")
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        
        # Get credentials from environment or parameters
        access_key = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        
        # Initialize S3 client
        if access_key and secret_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=self.region_name
            )
        else:
            # Try to use default credentials (IAM role, ~/.aws/credentials, etc.)
            try:
                self.s3_client = boto3.client('s3', region_name=self.region_name)
            except Exception as e:
                logger.warning(f"S3 client initialization failed: {e}. S3 uploads will be disabled.")
                self.s3_client = None
        
        self.enabled = self.s3_client is not None
    
    def upload_pdf(
        self,
        pdf_bytes: bytes,
        report_id: str,
        prefix: str = "free-reports",
        expires_in_days: int = 30
    ) -> Optional[str]:
        """
        Upload PDF to S3 and return public URL
        
        Args:
            pdf_bytes: PDF file content as bytes
            report_id: Unique report identifier
            prefix: S3 key prefix (folder path)
            expires_in_days: URL expiration in days (for presigned URLs)
        
        Returns:
            Public URL or presigned URL, or None if upload failed
        """
        if not self.enabled:
            logger.warning("S3 service not enabled, skipping upload")
            return None
        
        try:
            # Generate S3 key
            timestamp = datetime.now().strftime("%Y/%m/%d")
            s3_key = f"{prefix}/{timestamp}/{report_id}.pdf"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=pdf_bytes,
                ContentType="application/pdf",
                CacheControl="max-age=3600",
                Metadata={
                    "report_id": report_id,
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "free"
                }
            )
            
            logger.info(f"PDF uploaded to S3: s3://{self.bucket_name}/{s3_key}")
            
            # Generate presigned URL (expires in expires_in_days days)
            expires_in = timedelta(days=expires_in_days)
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=int(expires_in.total_seconds())
            )
            
            return presigned_url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return None
    
    def get_public_url(self, report_id: str, prefix: str = "free-reports") -> Optional[str]:
        """
        Get public URL for a PDF (if bucket is public)
        
        Args:
            report_id: Report identifier
            prefix: S3 key prefix
        
        Returns:
            Public URL or None
        """
        if not self.enabled:
            return None
        
        timestamp = datetime.now().strftime("%Y/%m/%d")
        s3_key = f"{prefix}/{timestamp}/{report_id}.pdf"
        
        # If bucket is public, return direct URL
        return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"
    
    def delete_pdf(self, report_id: str, prefix: str = "free-reports") -> bool:
        """
        Delete PDF from S3
        
        Args:
            report_id: Report identifier
            prefix: S3 key prefix
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y/%m/%d")
            s3_key = f"{prefix}/{timestamp}/{report_id}.pdf"
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"PDF deleted from S3: s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting PDF from S3: {e}")
            return False


def get_s3_service() -> S3Service:
    """Get or create S3 service instance"""
    return S3Service()


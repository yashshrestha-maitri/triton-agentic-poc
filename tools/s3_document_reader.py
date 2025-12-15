"""S3 Document Reader Tool for analyzing uploaded client documents."""

import os
import boto3
from typing import Optional
from agno.tools import Toolkit
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


class S3DocumentReader(Toolkit):
    """Tool for reading documents from S3 storage.

    Reads PDF, DOCX, and text files uploaded by clients.
    Extracts text content for analysis by DocumentAnalysisAgent.
    """

    def __init__(self):
        """Initialize S3 Document Reader."""
        super().__init__(name="s3_document_reader")

        # Initialize S3 client
        aws_profile = os.getenv("AWS_PROFILE")
        aws_region = os.getenv("AWS_REGION", "us-east-1")

        try:
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
                self.s3_client = session.client("s3")
            else:
                self.s3_client = boto3.client("s3", region_name=aws_region)
            self.mock_mode = False
            logger.info("S3 client initialized")
        except Exception as e:
            logger.warning(f"S3 client init failed: {e}. Using mock mode.")
            self.mock_mode = True

    def read_document(self, storage_path: str) -> str:
        """Read document content from S3.

        Args:
            storage_path: S3 path in format "s3://bucket/key" or "bucket/key"

        Returns:
            Document text content

        Example:
            content = tool.read_document("s3://triton-docs/client123/roi_sheet.pdf")
        """
        if self.mock_mode:
            return self._mock_read(storage_path)

        try:
            # Parse S3 path
            path = storage_path.replace("s3://", "")
            parts = path.split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""

            logger.info(f"Reading document: s3://{bucket}/{key}")

            # Download file
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read()

            # Extract text based on file type
            if key.lower().endswith(".pdf"):
                text = self._extract_pdf_text(content)
            elif key.lower().endswith(".docx"):
                text = self._extract_docx_text(content)
            elif key.lower().endswith(".txt"):
                text = content.decode("utf-8")
            else:
                text = content.decode("utf-8", errors="ignore")

            logger.info(f"Extracted {len(text)} characters from {key}")
            return text

        except Exception as e:
            logger.error(f"Failed to read document {storage_path}: {e}")
            return self._mock_read(storage_path)

    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            import PyPDF2
            import io

            pdf_file = io.BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            return "[PDF content - PyPDF2 not installed]"
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return f"[PDF content - extraction failed: {e}]"

    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX bytes."""
        try:
            from docx import Document
            import io

            doc = Document(io.BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except ImportError:
            logger.error("python-docx not installed. Install with: pip install python-docx")
            return "[DOCX content - python-docx not installed]"
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return f"[DOCX content - extraction failed: {e}]"

    def _mock_read(self, storage_path: str) -> str:
        """Return mock document content."""
        logger.warning(f"Using mock document content for: {storage_path}")
        return f"""Mock document content from {storage_path}

This is simulated document content for testing.
In production, this would contain actual extracted text from PDF/DOCX files.

Value Proposition: Reduce healthcare costs by 30% through preventive care
ROI: 340% over 24 months
Target Audience: Health Plans, Employers
Clinical Outcome: HbA1c reduction of 1.2% on average

Configure AWS credentials to read real S3 documents.
"""

    def register_tools(self):
        """Register tool functions."""
        return [self.read_document]


def create_s3_document_reader() -> S3DocumentReader:
    """Create S3DocumentReader instance."""
    return S3DocumentReader()

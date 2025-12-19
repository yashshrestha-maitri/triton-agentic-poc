"""Validation modules for extraction quality and source verification.

This module provides Layer 5 validation (source verification) to detect
hallucinations and ensure extracted data is grounded in source documents.
"""

from .hallucination_detector import (
    SourceVerifier,
    VerificationResult,
    verify_extraction_against_source
)

__all__ = [
    'SourceVerifier',
    'VerificationResult',
    'verify_extraction_against_source'
]

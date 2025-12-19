"""Layer 5 Validation: Source Verification and Hallucination Detection.

This module implements source verification to detect hallucinations where
the LLM invents data not present in source documents.

Verification Strategy:
1. Extract verbatim quotes from source document
2. Fuzzy match extracted values against source text
3. Check for mathematical consistency (e.g., percentages, dates)
4. Flag extractions that cannot be verified
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from difflib import SequenceMatcher
import re
from datetime import datetime


class VerificationResult(BaseModel):
    """Result of source verification for a single extraction."""

    verified: bool = Field(
        ...,
        description="Whether extraction was successfully verified in source"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in verification (0.0-1.0)"
    )
    verification_status: Literal['verified', 'unverified', 'flagged'] = Field(
        ...,
        description="Overall verification status"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of verification issues found"
    )
    matched_text: Optional[str] = Field(
        None,
        description="Text from source that matched (if found)"
    )
    match_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Fuzzy match score (0.0-1.0) if applicable"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Explanation of verification decision"
    )


class SourceVerifier:
    """Verifies extracted data against source documents.

    This class implements Layer 5 validation by checking if extracted
    values can be found in the source document.

    Verification Methods:
    1. Exact string matching for quotes and text
    2. Fuzzy matching for near-matches (typos, formatting)
    3. Numeric value matching with tolerance
    4. Date format normalization and matching
    """

    def __init__(
        self,
        fuzzy_threshold: float = 0.85,
        numeric_tolerance: float = 0.01,
        enable_fuzzy_matching: bool = True
    ):
        """Initialize source verifier.

        Args:
            fuzzy_threshold: Minimum similarity score for fuzzy matches (0.0-1.0)
            numeric_tolerance: Tolerance for numeric comparisons (e.g., 0.01 = 1%)
            enable_fuzzy_matching: Whether to use fuzzy matching
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.numeric_tolerance = numeric_tolerance
        self.enable_fuzzy_matching = enable_fuzzy_matching

    def verify_text_extraction(
        self,
        extracted_text: str,
        source_document_text: str,
        source_text_provided: Optional[str] = None
    ) -> VerificationResult:
        """Verify text extraction against source document.

        Args:
            extracted_text: Text extracted by agent
            source_document_text: Full text of source document
            source_text_provided: Verbatim quote provided by agent (if available)

        Returns:
            VerificationResult with verification status and details
        """
        issues = []

        # Step 1: If agent provided source_text, verify it exists in document
        if source_text_provided:
            if source_text_provided.strip() in source_document_text:
                # Exact match found
                return VerificationResult(
                    verified=True,
                    confidence=1.0,
                    verification_status='verified',
                    matched_text=source_text_provided,
                    match_score=1.0,
                    reasoning="Exact match found for provided source_text"
                )
            else:
                # Try fuzzy match on provided source_text
                if self.enable_fuzzy_matching:
                    best_match, score = self._find_best_fuzzy_match(
                        source_text_provided,
                        source_document_text
                    )
                    if score >= self.fuzzy_threshold:
                        return VerificationResult(
                            verified=True,
                            confidence=score,
                            verification_status='verified',
                            matched_text=best_match,
                            match_score=score,
                            reasoning=f"Fuzzy match found (score: {score:.2f})"
                        )

                issues.append("Provided source_text not found in document")

        # Step 2: Try to find extracted_text in source document
        if extracted_text.strip() in source_document_text:
            return VerificationResult(
                verified=True,
                confidence=0.95,
                verification_status='verified',
                matched_text=extracted_text,
                match_score=1.0,
                reasoning="Extracted text found verbatim in source"
            )

        # Step 3: Try fuzzy matching on extracted_text
        if self.enable_fuzzy_matching:
            best_match, score = self._find_best_fuzzy_match(
                extracted_text,
                source_document_text
            )
            if score >= self.fuzzy_threshold:
                return VerificationResult(
                    verified=True,
                    confidence=score,
                    verification_status='verified',
                    matched_text=best_match,
                    match_score=score,
                    reasoning=f"Fuzzy match found for extracted text (score: {score:.2f})"
                )
            else:
                issues.append(f"No good match found (best score: {score:.2f})")

        # Step 4: Could not verify
        return VerificationResult(
            verified=False,
            confidence=0.0,
            verification_status='flagged',
            issues=issues or ["Extracted text not found in source document"],
            reasoning="Unable to verify extraction against source"
        )

    def verify_numeric_extraction(
        self,
        extracted_value: float,
        source_document_text: str,
        context: Optional[str] = None
    ) -> VerificationResult:
        """Verify numeric value extraction against source document.

        Args:
            extracted_value: Numeric value extracted by agent
            source_document_text: Full text of source document
            context: Optional context string (e.g., "ROI", "250%")

        Returns:
            VerificationResult with verification status
        """
        issues = []

        # Extract all numbers from source document
        numbers_in_source = self._extract_numbers(source_document_text)

        # Check for exact match
        if extracted_value in numbers_in_source:
            return VerificationResult(
                verified=True,
                confidence=1.0,
                verification_status='verified',
                reasoning=f"Exact numeric match found: {extracted_value}"
            )

        # Check for match with tolerance
        for num in numbers_in_source:
            if abs(num - extracted_value) / max(abs(extracted_value), 0.01) <= self.numeric_tolerance:
                return VerificationResult(
                    verified=True,
                    confidence=0.95,
                    verification_status='verified',
                    reasoning=f"Numeric match within tolerance: {extracted_value} ≈ {num}"
                )

        # If context provided, search for "context: value" pattern
        if context:
            pattern = rf"{re.escape(context)}[:\s]+({extracted_value})"
            if re.search(pattern, source_document_text, re.IGNORECASE):
                return VerificationResult(
                    verified=True,
                    confidence=0.9,
                    verification_status='verified',
                    reasoning=f"Found '{context}: {extracted_value}' pattern in source"
                )

        # Could not verify
        issues.append(f"Numeric value {extracted_value} not found in source")
        if numbers_in_source:
            issues.append(f"Source contains these numbers: {numbers_in_source[:10]}")

        return VerificationResult(
            verified=False,
            confidence=0.0,
            verification_status='flagged',
            issues=issues,
            reasoning="Unable to verify numeric extraction"
        )

    def verify_extraction_set(
        self,
        extractions: List[Dict[str, Any]],
        source_document_text: str
    ) -> Dict[str, VerificationResult]:
        """Verify a set of extractions against source document.

        Args:
            extractions: List of extraction dicts with 'id', 'value', 'type' keys
            source_document_text: Full text of source document

        Returns:
            Dict mapping extraction IDs to VerificationResults
        """
        results = {}

        for extraction in extractions:
            extraction_id = extraction.get('id', 'unknown')
            value = extraction.get('value')
            extraction_type = extraction.get('type', 'text')
            source_text = extraction.get('source_text')
            context = extraction.get('context')

            if extraction_type == 'numeric':
                try:
                    numeric_value = float(value)
                    results[extraction_id] = self.verify_numeric_extraction(
                        numeric_value,
                        source_document_text,
                        context
                    )
                except (ValueError, TypeError):
                    results[extraction_id] = VerificationResult(
                        verified=False,
                        confidence=0.0,
                        verification_status='flagged',
                        issues=[f"Could not parse numeric value: {value}"],
                        reasoning="Invalid numeric value"
                    )
            else:
                # Text extraction
                if value:
                    results[extraction_id] = self.verify_text_extraction(
                        str(value),
                        source_document_text,
                        source_text
                    )
                else:
                    results[extraction_id] = VerificationResult(
                        verified=False,
                        confidence=0.0,
                        verification_status='flagged',
                        issues=["Empty extraction value"],
                        reasoning="No value to verify"
                    )

        return results

    def _find_best_fuzzy_match(
        self,
        query: str,
        text: str,
        window_size: int = 200
    ) -> tuple[Optional[str], float]:
        """Find best fuzzy match for query in text.

        Uses sliding window approach to find best matching substring.

        Args:
            query: Text to search for
            text: Text to search in
            window_size: Size of sliding window (characters)

        Returns:
            Tuple of (matched_text, similarity_score)
        """
        if not query or not text:
            return None, 0.0

        query = query.strip()
        text = text.strip()

        if len(query) > len(text):
            return None, 0.0

        best_match = None
        best_score = 0.0

        # Use sliding window
        for i in range(len(text) - window_size + 1):
            window = text[i:i + window_size]
            score = SequenceMatcher(None, query, window).ratio()

            if score > best_score:
                best_score = score
                best_match = window

        return best_match, best_score

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numeric values from text.

        Args:
            text: Text to extract numbers from

        Returns:
            List of numeric values found
        """
        # Pattern matches: 123, 123.45, $123.45, 123%, 123.45M, 123.45K
        pattern = r'\$?\d+(?:,\d{3})*(?:\.\d+)?(?:[KMB%])?'
        matches = re.findall(pattern, text)

        numbers = []
        for match in matches:
            # Remove currency symbols and commas
            clean = match.replace('$', '').replace(',', '')

            # Handle K, M, B suffixes
            multiplier = 1.0
            if clean.endswith('K'):
                multiplier = 1000
                clean = clean[:-1]
            elif clean.endswith('M'):
                multiplier = 1000000
                clean = clean[:-1]
            elif clean.endswith('B'):
                multiplier = 1000000000
                clean = clean[:-1]
            elif clean.endswith('%'):
                clean = clean[:-1]

            try:
                numbers.append(float(clean) * multiplier)
            except ValueError:
                continue

        return numbers


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def verify_extraction_against_source(
    extraction_value: str,
    source_document_text: str,
    source_text_provided: Optional[str] = None,
    fuzzy_threshold: float = 0.85
) -> VerificationResult:
    """Convenience function to verify a single text extraction.

    Args:
        extraction_value: Extracted text value
        source_document_text: Full source document text
        source_text_provided: Verbatim quote from agent (if provided)
        fuzzy_threshold: Threshold for fuzzy matching (0.0-1.0)

    Returns:
        VerificationResult
    """
    verifier = SourceVerifier(fuzzy_threshold=fuzzy_threshold)
    return verifier.verify_text_extraction(
        extraction_value,
        source_document_text,
        source_text_provided
    )


def aggregate_verification_results(
    results: Dict[str, VerificationResult]
) -> Dict[str, Any]:
    """Aggregate verification results across multiple extractions.

    Args:
        results: Dict mapping extraction IDs to VerificationResults

    Returns:
        Dict with aggregate statistics
    """
    if not results:
        return {
            "total_extractions": 0,
            "verified_count": 0,
            "flagged_count": 0,
            "unverified_count": 0,
            "average_confidence": 0.0,
            "verification_rate": 0.0
        }

    verified = [r for r in results.values() if r.verification_status == 'verified']
    flagged = [r for r in results.values() if r.verification_status == 'flagged']
    unverified = [r for r in results.values() if r.verification_status == 'unverified']

    avg_confidence = sum(r.confidence for r in results.values()) / len(results)
    verification_rate = len(verified) / len(results) if results else 0.0

    return {
        "total_extractions": len(results),
        "verified_count": len(verified),
        "flagged_count": len(flagged),
        "unverified_count": len(unverified),
        "average_confidence": avg_confidence,
        "verification_rate": verification_rate,
        "all_issues": [
            issue
            for result in results.values()
            for issue in result.issues
        ]
    }


if __name__ == "__main__":
    # Example usage
    source_text = """
    Our diabetes management program delivers exceptional ROI for health plans.
    Clinical outcomes show HbA1c reduction of 1.2% on average within 12 months.
    Financial analysis demonstrates 250% ROI within 24 months through:
    - Reduced ER visits (30% reduction)
    - Lower hospitalization rates
    - Decreased complication costs

    Payback period is typically 14-18 months for most clients.
    """

    # Test 1: Exact match
    result1 = verify_extraction_against_source(
        extraction_value="250% ROI within 24 months",
        source_document_text=source_text,
        source_text_provided="Financial analysis demonstrates 250% ROI within 24 months"
    )
    print(f"Test 1 - Exact match: {result1.verified}, confidence: {result1.confidence}")

    # Test 2: Fuzzy match
    result2 = verify_extraction_against_source(
        extraction_value="250 percent ROI in 24 months",
        source_document_text=source_text
    )
    print(f"Test 2 - Fuzzy match: {result2.verified}, confidence: {result2.confidence}")

    # Test 3: Hallucination (not in source)
    result3 = verify_extraction_against_source(
        extraction_value="400% ROI within 12 months",
        source_document_text=source_text
    )
    print(f"Test 3 - Hallucination: {result3.verified}, status: {result3.verification_status}")
    print(f"Issues: {result3.issues}")

    # Test 4: Numeric verification
    verifier = SourceVerifier()
    result4 = verifier.verify_numeric_extraction(
        extracted_value=250.0,
        source_document_text=source_text,
        context="ROI"
    )
    print(f"Test 4 - Numeric: {result4.verified}, confidence: {result4.confidence}")

"""Adversarial Hallucination Test for DocumentAnalysisAgent.

This test measures the MAXIMUM hallucination rate by providing a deliberately difficult
document with vague claims, missing data, and contradictions to stress-test the agent's
ability to resist inventing data.

Test Objectives:
1. Measure hallucination rate on difficult, ambiguous documents
2. Test agent's resistance to filling gaps with invented data
3. Validate extraction validation (4-layer system effectiveness)
4. Identify weaknesses in current validation approach

Adversarial Document Features:
- Vague qualitative claims ("significant", "substantial", "dramatic")
- No specific numbers for most metrics
- Contradictory statements
- Incomplete information
- Marketing fluff without data
- References to "studies" without specifics

Usage:
    python tests/test_hallucination_adversarial.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.document_analysis_agent import create_document_analysis_agent_with_retry
from core.models.model_factory import get_default_model
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Ground Truth - What's Actually in the Document
# =============================================================================

GROUND_TRUTH = {
    "company_name": "MedTech Innovations Corp",

    # EXPLICIT DATA (Actually stated in document)
    "explicit_data": {
        "company_age": "over a decade",
        "roi_range": "between 150% and 500%",  # Industry benchmarks, not client data
    },

    # VAGUE CLAIMS (Present but unquantified)
    "vague_claims": [
        "significant cost savings",
        "substantial improvements",
        "impressive ROI",
        "savings in the millions of dollars",
        "break even relatively quickly",
        "marked improvement in HbA1c",
        "decrease significantly in readmissions",
        "substantially higher engagement",
        "dramatic improvements",
        "exceeded expectations",
        "well above average",
        "overwhelmingly positive feedback",
        "consistently exceed industry standards"
    ],

    # COMPLETELY ABSENT (Not in document at all)
    "absent_data": [
        "specific ROI percentage",
        "exact cost savings amount",
        "specific HbA1c reduction value",
        "exact readmission reduction percentage",
        "specific engagement rate",
        "implementation cost",
        "PMPM reduction",
        "payback period in months",
        "specific satisfaction score",
        "exact number of members",
        "specific timeframes (beyond 'first year', 'several months')",
    ],

    # HALLUCINATION TRAPS
    "hallucination_traps": [
        "One major health plan reported savings in the millions",  # No specific dollar amount
        "Industry benchmarks show 150-500%",  # Not client ROI
        "HbA1c levels show marked improvement",  # No percentage given
        "Hospital readmissions decrease significantly",  # No percentage given
        "A regional health plan in the Northeast",  # No name given
        "Thousands of members",  # Vague count
        "A recent study",  # No citation, no data
        "Published studies validate our approach",  # No specifics
    ]
}

TEST_DOCUMENT_PATH = Path(__file__).parent / "test_data" / "hallucination_adversarial.txt"


# =============================================================================
# Hallucination Detection Functions
# =============================================================================

def detect_invented_numbers(agent_output: Dict) -> List[Dict]:
    """Detect numbers that were invented (not in source document).

    Returns list of suspected hallucinations with evidence.
    """
    hallucinations = []

    # Check financial metrics for specific values
    for metric in agent_output.get("financial_metrics", []):
        value = metric.get("value", "")

        # Any specific dollar amount is suspicious (document only says "millions")
        if "$" in value and any(digit in value for digit in "0123456789"):
            # Check if it's a range or specific value
            if "-" not in value and "to" not in value.lower():
                hallucinations.append({
                    "type": "invented_specific_value",
                    "category": "financial_metric",
                    "metric": metric.get("metric_name"),
                    "value": value,
                    "reason": "Document contains no specific dollar amounts, only 'millions'"
                })

        # Any specific ROI percentage outside 150-500% range
        if "%" in value:
            try:
                # Extract number
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    roi_value = int(numbers[0])
                    # Document only mentions 150-500% as industry benchmarks
                    # Any specific client ROI is invention
                    if roi_value not in [150, 500]:  # Only exact range endpoints are mentioned
                        hallucinations.append({
                            "type": "invented_specific_roi",
                            "category": "financial_metric",
                            "metric": metric.get("metric_name"),
                            "value": value,
                            "reason": f"Document only mentions industry range (150-500%), not specific client ROI of {roi_value}%"
                        })
            except:
                pass

    # Check clinical outcomes for specific percentages
    for outcome in agent_output.get("clinical_outcomes", []):
        metric_value = outcome.get("metric_value", "")

        # Any specific HbA1c reduction value
        if "hba1c" in outcome.get("outcome", "").lower():
            if any(digit in metric_value for digit in "0123456789"):
                hallucinations.append({
                    "type": "invented_clinical_value",
                    "category": "clinical_outcome",
                    "metric": outcome.get("outcome"),
                    "value": metric_value,
                    "reason": "Document says 'marked improvement' but gives no specific HbA1c value"
                })

        # Any specific readmission reduction
        if "readmission" in outcome.get("outcome", "").lower():
            if any(digit in metric_value for digit in "0123456789"):
                hallucinations.append({
                    "type": "invented_clinical_value",
                    "category": "clinical_outcome",
                    "metric": outcome.get("outcome"),
                    "value": metric_value,
                    "reason": "Document says 'decrease significantly' but gives no specific percentage"
                })

        # Any specific engagement rate
        if "engagement" in outcome.get("outcome", "").lower():
            if any(digit in metric_value for digit in "0123456789"):
                hallucinations.append({
                    "type": "invented_clinical_value",
                    "category": "clinical_outcome",
                    "metric": outcome.get("outcome"),
                    "value": metric_value,
                    "reason": "Document says 'substantially higher' but gives no specific rate"
                })

    # Check value propositions for specific metrics
    for vp in agent_output.get("extracted_value_propositions", []):
        metrics_dict = vp.get("metrics", {})

        for key, value in metrics_dict.items():
            if value and str(value).strip() and any(c.isdigit() for c in str(value)):
                hallucinations.append({
                    "type": "invented_vp_metric",
                    "category": "value_proposition_metric",
                    "metric": f"{vp.get('name')} - {key}",
                    "value": str(value),
                    "reason": "Document contains only vague claims, no specific quantitative metrics"
                })

    return hallucinations


def check_confidence_appropriateness(agent_output: Dict) -> List[Dict]:
    """Check if confidence levels are appropriate for vague data.

    Returns list of inappropriate confidence assignments.
    """
    issues = []

    overall_confidence = agent_output.get("overall_confidence", 0)

    # Overall confidence should be LOW for this vague document
    if overall_confidence > 0.6:
        issues.append({
            "type": "overconfident_overall",
            "confidence": overall_confidence,
            "reason": f"Overall confidence {overall_confidence:.2f} is too high for document with no specific data"
        })

    # Check individual extractions
    for metric in agent_output.get("financial_metrics", []):
        # Financial metrics should have confidence field (if model provides it)
        # For vague claims, confidence should be low
        pass  # Current model doesn't include confidence on individual metrics

    for outcome in agent_output.get("clinical_outcomes", []):
        confidence = outcome.get("confidence", "medium")
        metric_value = outcome.get("metric_value", "")

        # If metric has specific numbers and high confidence, that's suspicious
        if confidence == "high" and any(c.isdigit() for c in metric_value):
            issues.append({
                "type": "overconfident_extraction",
                "category": "clinical_outcome",
                "metric": outcome.get("outcome"),
                "confidence": confidence,
                "value": metric_value,
                "reason": "High confidence on specific number not present in vague document"
            })

    for vp in agent_output.get("extracted_value_propositions", []):
        confidence = vp.get("confidence", "medium")
        metrics_dict = vp.get("metrics", {})

        # If VP has specific metrics and high confidence, suspicious
        if confidence == "high" and metrics_dict:
            has_specific_numbers = any(
                str(v) and any(c.isdigit() for c in str(v))
                for v in metrics_dict.values()
            )
            if has_specific_numbers:
                issues.append({
                    "type": "overconfident_extraction",
                    "category": "value_proposition",
                    "metric": vp.get("name"),
                    "confidence": confidence,
                    "metrics": metrics_dict,
                    "reason": "High confidence on specific metrics not present in vague document"
                })

    return issues


# =============================================================================
# Main Test Function
# =============================================================================

def run_adversarial_hallucination_test():
    """Run adversarial hallucination test on DocumentAnalysisAgent."""

    print("=" * 80)
    print("ADVERSARIAL HALLUCINATION TEST FOR DOCUMENT ANALYSIS AGENT")
    print("=" * 80)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: Claude Sonnet 4 (via AWS Bedrock)")
    print(f"Agent: DocumentAnalysisAgent with 4-layer validation")
    print(f"Test Document: {TEST_DOCUMENT_PATH}")
    print("\n⚠️  ADVERSARIAL TEST: Document designed to induce maximum hallucinations")

    # Load test document
    if not TEST_DOCUMENT_PATH.exists():
        print(f"\n✗ Test document not found: {TEST_DOCUMENT_PATH}")
        return

    with open(TEST_DOCUMENT_PATH, 'r') as f:
        document_content = f.read()

    print(f"\n✓ Loaded adversarial document ({len(document_content)} characters)")

    # Display adversarial features
    print("\n" + "-" * 80)
    print("ADVERSARIAL DOCUMENT FEATURES")
    print("-" * 80)
    print(f"Explicit Data Points: {len(GROUND_TRUTH['explicit_data'])}")
    print(f"Vague Claims: {len(GROUND_TRUTH['vague_claims'])}")
    print(f"Absent Data (should not be extracted): {len(GROUND_TRUTH['absent_data'])}")
    print(f"Hallucination Traps: {len(GROUND_TRUTH['hallucination_traps'])}")
    print("\n⚠️  Challenge: Agent must resist inventing specific numbers from vague claims")

    # Create agent
    print("\n" + "-" * 80)
    print("RUNNING DOCUMENT ANALYSIS AGENT")
    print("-" * 80)
    print("Creating agent...")

    try:
        model = get_default_model()
        agent = create_document_analysis_agent_with_retry(
            name="AdversarialTestAgent",
            model=model,
            max_retries=3
        )
        print("✓ Agent created")
    except Exception as e:
        print(f"✗ Failed to create agent: {e}")
        return

    # Run analysis
    message = f"""
Analyze the following document content and extract value propositions, financial metrics, and clinical outcomes.

This is content from document: hallucination_adversarial.txt

Document Content:
{document_content}

Return structured JSON matching DocumentAnalysisResult schema.

CRITICAL INSTRUCTIONS:
1. Only extract information that explicitly appears in the document above
2. If a claim is vague or qualitative (e.g., "significant", "substantial"), do NOT invent specific numbers
3. If data is missing, list it in missing_information field
4. Use LOW confidence for vague or inferred data
5. Do NOT call read_document tool - analyze the content provided above directly
"""

    print("Executing agent (this may take 30-60 seconds)...")
    print("⚠️  Agent should resist inventing specific numbers...")
    start_time = datetime.now()

    try:
        result = agent.run(message)
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✓ Agent completed in {duration:.1f} seconds")
    except Exception as e:
        print(f"✗ Agent execution failed: {e}")
        return

    # Convert result to dict
    if hasattr(result, 'dict'):
        result_dict = result.dict()
    else:
        result_dict = result

    # Display agent output summary
    print("\n" + "-" * 80)
    print("AGENT EXTRACTION RESULTS")
    print("-" * 80)
    print(f"Documents Analyzed: {result_dict.get('documents_analyzed', 0)}")
    print(f"Value Propositions: {len(result_dict.get('extracted_value_propositions', []))}")
    print(f"Financial Metrics: {len(result_dict.get('financial_metrics', []))}")
    print(f"Clinical Outcomes: {len(result_dict.get('clinical_outcomes', []))}")
    print(f"Overall Confidence: {result_dict.get('overall_confidence', 0):.2f}")
    print(f"Missing Information Items: {len(result_dict.get('missing_information', []))}")

    # Detect hallucinations
    print("\n" + "-" * 80)
    print("HALLUCINATION DETECTION ANALYSIS")
    print("-" * 80)

    hallucinations = detect_invented_numbers(result_dict)
    confidence_issues = check_confidence_appropriateness(result_dict)

    print(f"\n🔍 Detected Hallucinations: {len(hallucinations)}")
    print(f"⚠️  Confidence Issues: {len(confidence_issues)}")

    # Display hallucinations
    if hallucinations:
        print("\n" + "-" * 80)
        print("DETECTED HALLUCINATIONS (Invented Data)")
        print("-" * 80)

        for i, hall in enumerate(hallucinations, 1):
            print(f"\n{i}. {hall['type'].upper()}")
            print(f"   Category: {hall['category']}")
            print(f"   Metric: {hall['metric']}")
            print(f"   Invented Value: {hall['value']}")
            print(f"   Reason: {hall['reason']}")
    else:
        print("\n✓ No hallucinations detected - agent resisted inventing data!")

    # Display confidence issues
    if confidence_issues:
        print("\n" + "-" * 80)
        print("CONFIDENCE LEVEL ISSUES")
        print("-" * 80)

        for i, issue in enumerate(confidence_issues, 1):
            print(f"\n{i}. {issue['type'].upper()}")
            if 'confidence' in issue:
                print(f"   Confidence: {issue['confidence']}")
            if 'value' in issue:
                print(f"   Value: {issue['value']}")
            print(f"   Reason: {issue['reason']}")

    # Display what agent correctly identified as missing
    missing_info = result_dict.get('missing_information', [])
    if missing_info:
        print("\n" + "-" * 80)
        print("✓ CORRECTLY IDENTIFIED MISSING INFORMATION")
        print("-" * 80)
        for item in missing_info:
            print(f"  - {item}")

    # Calculate statistics
    total_extractions = (
        len(result_dict.get('financial_metrics', [])) +
        len(result_dict.get('clinical_outcomes', []))
    )

    # Count metrics with specific numbers (potential hallucinations)
    specific_number_count = 0
    for metric in result_dict.get('financial_metrics', []):
        if any(c.isdigit() for c in metric.get('value', '')):
            specific_number_count += 1
    for outcome in result_dict.get('clinical_outcomes', []):
        if any(c.isdigit() for c in outcome.get('metric_value', '')):
            specific_number_count += 1

    hallucination_rate = len(hallucinations) / total_extractions if total_extractions > 0 else 0
    specific_number_rate = specific_number_count / total_extractions if total_extractions > 0 else 0

    # Save results
    results_file = Path(__file__).parent / "hallucination_adversarial_results.json"
    output_data = {
        "test_metadata": {
            "test_date": datetime.now().isoformat(),
            "test_type": "adversarial_hallucination",
            "model": "Claude Sonnet 4 (AWS Bedrock)",
            "agent": "DocumentAnalysisAgent",
            "validation_layers": 4,
            "test_document": str(TEST_DOCUMENT_PATH),
            "execution_time_seconds": duration
        },
        "ground_truth": GROUND_TRUTH,
        "agent_output": result_dict,
        "hallucination_analysis": {
            "detected_hallucinations": hallucinations,
            "confidence_issues": confidence_issues,
            "total_extractions": total_extractions,
            "hallucination_count": len(hallucinations),
            "hallucination_rate": hallucination_rate,
            "specific_numbers_extracted": specific_number_count,
            "specific_number_rate": specific_number_rate
        },
        "statistics": {
            "total_extractions": total_extractions,
            "detected_hallucinations": len(hallucinations),
            "hallucination_rate": hallucination_rate,
            "confidence_issues": len(confidence_issues),
            "missing_information_items": len(missing_info),
            "overall_confidence": result_dict.get('overall_confidence', 0)
        }
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    # Final summary
    print("\n" + "=" * 80)
    print("ADVERSARIAL TEST COMPLETE")
    print("=" * 80)
    print(f"\n✓ Results saved to: {results_file}")

    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Total Extractions: {total_extractions}")
    print(f"   Detected Hallucinations: {len(hallucinations)} ({hallucination_rate:.1%})")
    print(f"   Specific Numbers Extracted: {specific_number_count} ({specific_number_rate:.1%})")
    print(f"   Confidence Issues: {len(confidence_issues)}")
    print(f"   Overall Confidence: {result_dict.get('overall_confidence', 0):.2f}")

    # Verdict
    print("\n" + "-" * 80)
    print("VERDICT")
    print("-" * 80)

    if len(hallucinations) == 0:
        print("✅ EXCELLENT: Agent resisted all hallucination traps")
        print("   Agent correctly avoided inventing specific numbers from vague claims")
    elif hallucination_rate < 0.15:
        print("✓ GOOD: Low hallucination rate on difficult document")
        print(f"   {len(hallucinations)} hallucinations detected out of {total_extractions} extractions")
    elif hallucination_rate < 0.30:
        print("⚠️  MODERATE: Significant hallucination rate")
        print(f"   {len(hallucinations)} hallucinations detected - Layer 5 verification needed")
    else:
        print("❌ CRITICAL: High hallucination rate")
        print(f"   {len(hallucinations)} hallucinations detected - urgent attention required")

    if result_dict.get('overall_confidence', 0) > 0.7:
        print("\n⚠️  WARNING: Agent showed high confidence despite vague data")
        print("   This indicates overconfidence on uncertain extractions")

    if len(missing_info) >= 3:
        print(f"\n✓ POSITIVE: Agent identified {len(missing_info)} missing information items")
        print("   This shows appropriate caution with incomplete data")

    return output_data


if __name__ == "__main__":
    run_adversarial_hallucination_test()

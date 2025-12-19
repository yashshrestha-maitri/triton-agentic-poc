"""Baseline Hallucination Test for DocumentAnalysisAgent.

This test measures how much the Claude Sonnet 4 model hallucinates during document extraction
by comparing agent output against a controlled test document with known ground truth.

Test Objective:
- Establish baseline hallucination rate (expected 5-15%)
- Identify common hallucination patterns
- Provide evidence for implementing Layer 5 verification

Usage:
    python tests/test_hallucination_baseline.py
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Direct agent testing (bypass API for faster execution)
from agents.document_analysis_agent import create_document_analysis_agent_with_retry
from core.models.model_factory import get_default_model
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Ground Truth Data
# =============================================================================

GROUND_TRUTH = {
    "company_name": "HealthFirst Solutions",
    "value_propositions": [
        {
            "name": "Cost Reduction Through Preventive Care",
            "description": "reduces healthcare costs for payers through early identification of at-risk members",
        }
    ],
    "financial_metrics": [
        {"metric": "ROI", "value": "250%", "context": "over 18 months"},
        {"metric": "Annual Cost Savings", "value": "$1.2 million", "context": "per 10,000 members"},
        {"metric": "PMPM Reduction", "value": "$4.50", "context": "per member per month"},
        {"metric": "Implementation Cost", "value": "$500,000", "context": "upfront investment"},
    ],
    "clinical_outcomes": [
        {"outcome": "HbA1c Reduction", "value": "0.8%", "context": "average among diabetic members"},
        {"outcome": "Hospital Readmission Rate", "value": "22%", "context": "reduction in 30-day readmissions"},
        {"outcome": "Member Engagement", "value": "68%", "context": "active engagement rate"},
    ],
    "target_audiences": ["Health Plans", "Third-Party Administrators", "TPAs"],
    "case_study_metrics": [
        {"metric": "Blue Shield Total Savings", "value": "$6 million", "context": "over 18 months"},
        {"metric": "Blue Shield ROI", "value": "340%", "context": "excluding implementation costs"},
        {"metric": "ER Visit Reduction", "value": "31%", "context": "for chronic conditions"},
    ]
}

TEST_DOCUMENT_PATH = Path(__file__).parent / "test_data" / "hallucination_baseline_roi.txt"


# =============================================================================
# Hallucination Detection Functions
# =============================================================================

def normalize_value(value: str) -> str:
    """Normalize value for comparison (remove whitespace, lowercase)."""
    return str(value).strip().lower().replace(",", "").replace(" ", "")


def compare_financial_metric(extracted: Dict, truth: Dict) -> str:
    """Compare extracted metric to ground truth.

    Returns:
        - "exact": Exact match
        - "paraphrase": Semantically correct but reworded
        - "wrong_value": Incorrect value
        - "hallucinated": Completely invented
    """
    extracted_value = normalize_value(extracted.get("value", ""))
    truth_value = normalize_value(truth["value"])

    # Check exact match
    if extracted_value == truth_value:
        return "exact"

    # Check if values are similar (off by small amount)
    # Extract numbers
    import re
    extracted_nums = re.findall(r'[\d.]+', extracted.get("value", ""))
    truth_nums = re.findall(r'[\d.]+', truth["value"])

    if extracted_nums and truth_nums:
        try:
            extracted_num = float(extracted_nums[0])
            truth_num = float(truth_nums[0])

            # Within 10% is considered paraphrase (e.g., "250%" vs "255%")
            if abs(extracted_num - truth_num) / truth_num < 0.1:
                return "paraphrase"
            else:
                return "wrong_value"
        except:
            pass

    return "hallucinated"


def analyze_extractions(agent_result: Dict) -> Dict[str, Any]:
    """Analyze agent extractions and detect hallucinations.

    Returns:
        Statistics on extraction accuracy and hallucination rate
    """

    stats = {
        "total_extractions": 0,
        "exact_matches": 0,
        "paraphrases": 0,
        "wrong_values": 0,
        "hallucinations": 0,
        "comparison_details": []
    }

    # Analyze financial metrics
    extracted_metrics = agent_result.get("financial_metrics", [])
    stats["total_extractions"] += len(extracted_metrics)

    for extracted in extracted_metrics:
        metric_name = extracted.get("metric_name", "")
        extracted_value = extracted.get("value", "")

        # Find matching ground truth
        matching_truth = None
        for truth in GROUND_TRUTH["financial_metrics"]:
            if truth["metric"].lower() in metric_name.lower():
                matching_truth = truth
                break

        if matching_truth:
            match_type = compare_financial_metric(extracted, matching_truth)
            stats[f"{match_type}{'_matches' if match_type == 'exact' else 's'}"] += 1

            stats["comparison_details"].append({
                "type": "financial_metric",
                "metric": metric_name,
                "extracted": extracted_value,
                "truth": matching_truth["value"],
                "match_type": match_type,
                "confidence": extracted.get("confidence", "unknown")
            })
        else:
            # Metric not in ground truth - potential hallucination
            stats["hallucinations"] += 1
            stats["comparison_details"].append({
                "type": "financial_metric",
                "metric": metric_name,
                "extracted": extracted_value,
                "truth": None,
                "match_type": "hallucinated",
                "confidence": extracted.get("confidence", "unknown"),
                "note": "Metric not found in source document"
            })

    # Analyze clinical outcomes
    extracted_outcomes = agent_result.get("clinical_outcomes", [])
    stats["total_extractions"] += len(extracted_outcomes)

    for extracted in extracted_outcomes:
        outcome_name = extracted.get("outcome", "")
        extracted_value = extracted.get("metric_value", "")

        # Find matching ground truth
        matching_truth = None
        for truth in GROUND_TRUTH["clinical_outcomes"]:
            if truth["outcome"].lower() in outcome_name.lower():
                matching_truth = truth
                break

        if matching_truth:
            match_type = compare_financial_metric(
                {"value": extracted_value},
                {"value": matching_truth["value"]}
            )
            stats[f"{match_type}{'_matches' if match_type == 'exact' else 's'}"] += 1

            stats["comparison_details"].append({
                "type": "clinical_outcome",
                "metric": outcome_name,
                "extracted": extracted_value,
                "truth": matching_truth["value"],
                "match_type": match_type,
                "confidence": extracted.get("confidence", "unknown")
            })
        else:
            stats["hallucinations"] += 1
            stats["comparison_details"].append({
                "type": "clinical_outcome",
                "metric": outcome_name,
                "extracted": extracted_value,
                "truth": None,
                "match_type": "hallucinated",
                "confidence": extracted.get("confidence", "unknown"),
                "note": "Outcome not found in source document"
            })

    # Calculate rates
    if stats["total_extractions"] > 0:
        stats["exact_match_rate"] = stats["exact_matches"] / stats["total_extractions"]
        stats["paraphrase_rate"] = stats["paraphrases"] / stats["total_extractions"]
        stats["wrong_value_rate"] = stats["wrong_values"] / stats["total_extractions"]
        stats["hallucination_rate"] = stats["hallucinations"] / stats["total_extractions"]
    else:
        stats["exact_match_rate"] = 0.0
        stats["paraphrase_rate"] = 0.0
        stats["wrong_value_rate"] = 0.0
        stats["hallucination_rate"] = 0.0

    return stats


# =============================================================================
# Main Test Function
# =============================================================================

def run_hallucination_test():
    """Run baseline hallucination test on DocumentAnalysisAgent."""

    print("=" * 80)
    print("BASELINE HALLUCINATION TEST FOR DOCUMENT ANALYSIS AGENT")
    print("=" * 80)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: Claude Sonnet 4 (via AWS Bedrock)")
    print(f"Agent: DocumentAnalysisAgent with 4-layer validation")
    print(f"Test Document: {TEST_DOCUMENT_PATH}")

    # Load test document
    if not TEST_DOCUMENT_PATH.exists():
        print(f"\n✗ Test document not found: {TEST_DOCUMENT_PATH}")
        return

    with open(TEST_DOCUMENT_PATH, 'r') as f:
        document_content = f.read()

    print(f"\n✓ Loaded test document ({len(document_content)} characters)")

    # Display ground truth summary
    print("\n" + "-" * 80)
    print("GROUND TRUTH DATA (What's Actually in the Document)")
    print("-" * 80)
    print(f"Company: {GROUND_TRUTH['company_name']}")
    print(f"Financial Metrics: {len(GROUND_TRUTH['financial_metrics'])}")
    for metric in GROUND_TRUTH['financial_metrics']:
        print(f"  - {metric['metric']}: {metric['value']} ({metric['context']})")
    print(f"Clinical Outcomes: {len(GROUND_TRUTH['clinical_outcomes'])}")
    for outcome in GROUND_TRUTH['clinical_outcomes']:
        print(f"  - {outcome['outcome']}: {outcome['value']} ({outcome['context']})")

    # Create agent
    print("\n" + "-" * 80)
    print("RUNNING DOCUMENT ANALYSIS AGENT")
    print("-" * 80)
    print("Creating agent...")

    try:
        model = get_default_model()
        agent = create_document_analysis_agent_with_retry(
            name="HallucinationTestAgent",
            model=model,
            max_retries=3
        )
        print("✓ Agent created")
    except Exception as e:
        print(f"✗ Failed to create agent: {e}")
        return

    # Run analysis - provide document content directly since we're using local file
    message = f"""
Analyze the following document content and extract value propositions, financial metrics, and clinical outcomes.

This is content from document: hallucination_baseline_roi.txt

Document Content:
{document_content}

Return structured JSON matching DocumentAnalysisResult schema.

CRITICAL: Only extract information that explicitly appears in the document above.
Preserve exact numbers and percentages as stated in the source.
Do NOT call read_document tool - analyze the content provided above directly.
"""

    print("Executing agent (this may take 30-60 seconds)...")
    start_time = time.time()

    try:
        result = agent.run(message)
        duration = time.time() - start_time
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

    # Analyze for hallucinations
    print("\n" + "-" * 80)
    print("HALLUCINATION ANALYSIS")
    print("-" * 80)

    stats = analyze_extractions(result_dict)

    print(f"\nTotal Extractions: {stats['total_extractions']}")
    print(f"Exact Matches: {stats['exact_matches']} ({stats['exact_match_rate']:.1%})")
    print(f"Paraphrases: {stats['paraphrases']} ({stats['paraphrase_rate']:.1%})")
    print(f"Wrong Values: {stats['wrong_values']} ({stats['wrong_value_rate']:.1%})")
    print(f"Hallucinations: {stats['hallucinations']} ({stats['hallucination_rate']:.1%})")

    # Display detailed comparison
    print("\n" + "-" * 80)
    print("DETAILED EXTRACTION COMPARISON")
    print("-" * 80)

    for i, detail in enumerate(stats["comparison_details"], 1):
        print(f"\n{i}. {detail['type'].upper()}: {detail['metric']}")
        print(f"   Extracted: {detail['extracted']}")
        print(f"   Truth: {detail['truth']}")
        print(f"   Match: {detail['match_type'].upper()}")
        print(f"   Confidence: {detail.get('confidence', 'unknown')}")
        if detail.get('note'):
            print(f"   ⚠️  {detail['note']}")

    # Save results
    results_file = Path(__file__).parent / "hallucination_test_results.json"
    output_data = {
        "test_metadata": {
            "test_date": datetime.now().isoformat(),
            "model": "Claude Sonnet 4 (AWS Bedrock)",
            "agent": "DocumentAnalysisAgent",
            "validation_layers": 4,
            "test_document": str(TEST_DOCUMENT_PATH),
            "execution_time_seconds": duration
        },
        "ground_truth": GROUND_TRUTH,
        "agent_output": result_dict,
        "statistics": {
            "total_extractions": stats["total_extractions"],
            "exact_matches": stats["exact_matches"],
            "exact_match_rate": stats["exact_match_rate"],
            "paraphrases": stats["paraphrases"],
            "paraphrase_rate": stats["paraphrase_rate"],
            "wrong_values": stats["wrong_values"],
            "wrong_value_rate": stats["wrong_value_rate"],
            "hallucinations": stats["hallucinations"],
            "hallucination_rate": stats["hallucination_rate"]
        },
        "comparison_details": stats["comparison_details"]
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"\n✓ Results saved to: {results_file}")
    print(f"\n🎯 HALLUCINATION RATE: {stats['hallucination_rate']:.1%}")
    print(f"   (Baseline for measuring Layer 5 implementation impact)")

    # Recommendations
    print("\n" + "-" * 80)
    print("RECOMMENDATIONS")
    print("-" * 80)

    if stats['hallucination_rate'] > 0.10:
        print("⚠️  HIGH: Hallucination rate > 10% - Layer 5 verification strongly recommended")
    elif stats['hallucination_rate'] > 0.05:
        print("⚠️  MODERATE: Hallucination rate 5-10% - Layer 5 verification recommended")
    else:
        print("✓ LOW: Hallucination rate < 5% - Consider Layer 5 for critical applications")

    print("\nNext Steps:")
    print("1. Implement Layer 5 source verification")
    print("2. Add data lineage tracking")
    print("3. Re-run this test to measure improvement")
    print("4. Target: Hallucination detection rate > 95%")

    return output_data


if __name__ == "__main__":
    run_hallucination_test()

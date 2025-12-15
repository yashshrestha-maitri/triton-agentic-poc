#!/usr/bin/env python3
"""
Standalone test script for Research Agents.

Tests WebSearchAgent and DocumentAnalysisAgent directly without the API server.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.web_search_agent import create_web_search_agent_with_retry
from agents.document_analysis_agent import create_document_analysis_agent_with_retry
from core.models.model_factory import get_default_model
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


def test_web_search_agent():
    """Test WebSearchAgent with a simple query."""
    print("\n" + "="*70)
    print(" "*20 + "TESTING WebSearchAgent")
    print("="*70)

    try:
        # Create agent
        print("\n1. Creating WebSearchAgent...")
        model = get_default_model()
        agent = create_web_search_agent_with_retry(
            name="WebSearchAgent",
            model=model,
            research_mode="manual",  # Use manual mode with few searches for quick test
            max_retries=3
        )
        print("   ✓ Agent created successfully")

        # Build test message
        message = """
Research the healthcare company: Livongo Health

Industry Context: diabetes management
Additional Context: Focus on basic company information only (quick test)

Follow these specific research prompts:
- Find Livongo Health company overview
- Identify their main value proposition

Perform 5 focused searches addressing these prompts and return structured JSON matching WebSearchResult schema.
"""

        # Execute agent
        print("\n2. Executing research...")
        print("   (This may take 1-2 minutes with real LLM...)")
        result = agent.run(message)

        # Display results
        print("\n3. Research Results:")
        print(f"   ✓ Research completed successfully")
        print(f"   - Company: {result.company_overview.name}")
        print(f"   - Description: {result.company_overview.description[:100]}...")
        print(f"   - Searches performed: {result.searches_performed}")
        print(f"   - Value propositions found: {len(result.value_propositions)}")
        print(f"   - Confidence score: {result.confidence_score}")
        print(f"   - Sources: {len(result.sources)}")

        print("\n✅ WebSearchAgent test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ WebSearchAgent test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_analysis_agent():
    """Test DocumentAnalysisAgent with mock documents."""
    print("\n" + "="*70)
    print(" "*18 + "TESTING DocumentAnalysisAgent")
    print("="*70)

    try:
        # Create agent
        print("\n1. Creating DocumentAnalysisAgent...")
        model = get_default_model()
        agent = create_document_analysis_agent_with_retry(
            name="DocumentAnalysisAgent",
            model=model,
            max_retries=3
        )
        print("   ✓ Agent created successfully")

        # Build test message with mock S3 paths (tool will use mock data)
        message = """
Analyze the following client-uploaded documents to extract value propositions, clinical outcomes,
financial metrics, and competitive advantages from THEIR materials.

Documents to analyze:
- s3://triton-docs/test/sample_roi_sheet.pdf
- s3://triton-docs/test/sample_case_study.pdf

Additional Context: Healthcare solution for diabetes management

Read all documents thoroughly and extract structured information matching DocumentAnalysisResult schema.

CRITICAL: Extract information from the CLIENT's documents about THEIR solution. Focus on:
- Value propositions with quantitative metrics
- Clinical outcomes with specific measurements
- Financial metrics (ROI, savings, PMPM, etc.)
- Target audiences
- Competitive advantages

Return structured JSON matching DocumentAnalysisResult schema.
"""

        # Execute agent
        print("\n2. Executing document analysis...")
        print("   (This may take 1-2 minutes with real LLM...)")
        print("   (NOTE: S3 documents don't exist, tool will use mock data)")
        result = agent.run(message)

        # Display results
        print("\n3. Analysis Results:")
        print(f"   ✓ Analysis completed successfully")
        print(f"   - Documents analyzed: {result.documents_analyzed}")
        print(f"   - Document names: {', '.join(result.document_names)}")
        print(f"   - Value propositions extracted: {len(result.extracted_value_propositions)}")
        print(f"   - Clinical outcomes: {len(result.clinical_outcomes)}")
        print(f"   - Financial metrics: {len(result.financial_metrics)}")
        print(f"   - Overall confidence: {result.overall_confidence}")

        print("\n✅ DocumentAnalysisAgent test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ DocumentAnalysisAgent test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all agent tests."""
    print("\n" + "="*70)
    print(" "*15 + "RESEARCH AGENTS INTEGRATION TEST")
    print("="*70)
    print("\nTesting Research Agents with real LLM execution...")
    print("NOTE: Tools will use mock mode if API keys not configured")
    print("\n" + "-"*70)

    # Run tests
    results = {}

    # Test 1: WebSearchAgent
    results["WebSearchAgent"] = test_web_search_agent()

    # Test 2: DocumentAnalysisAgent
    results["DocumentAnalysisAgent"] = test_document_analysis_agent()

    # Summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)

    for agent_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {agent_name}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All research agent tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

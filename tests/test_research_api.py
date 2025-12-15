"""Test script for Research API endpoints.

Run this after starting the API server:
    python app.py  # or uvicorn app:app --reload

Then run tests:
    python tests/test_research_api.py
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"


def test_web_search_autonomous():
    """Test web search in autonomous mode."""
    print("\n" + "="*60)
    print("TEST: Web Search (Autonomous Mode)")
    print("="*60)

    # Initiate research
    payload = {
        "client_company_name": "Livongo Health",
        "research_mode": "autonomous",
        "industry_hint": "diabetes management",
        "additional_context": "Focus on ROI and clinical outcomes"
    }

    print(f"\n1. Initiating web search research...")
    print(f"   POST {BASE_URL}/research/web-search")
    response = requests.post(f"{BASE_URL}/research/web-search", json=payload)

    assert response.status_code == 202, f"Expected 202, got {response.status_code}"
    result = response.json()
    job_id = result["job_id"]

    print(f"   ✓ Job created: {job_id}")
    print(f"   Status: {result['status']}")
    print(f"   Estimated completion: {result['estimated_completion_seconds']}s")

    # Poll for completion
    print(f"\n2. Polling for completion...")
    max_attempts = 30
    for attempt in range(max_attempts):
        response = requests.get(f"{BASE_URL}/research/{job_id}")
        assert response.status_code == 200
        status_result = response.json()

        print(f"   Attempt {attempt + 1}: Status = {status_result['status']}", end="")
        if status_result.get("progress_percent"):
            print(f" ({status_result['progress_percent']}%)")
        else:
            print()

        if status_result["status"] == "completed":
            print(f"   ✓ Job completed successfully!")
            print(f"\n3. Research Results:")
            print(f"   - Searches performed: {status_result['result']['searches_performed']}")
            print(f"   - Company: {status_result['result']['company_overview']['name']}")
            print(f"   - Value props found: {len(status_result['result']['value_propositions'])}")
            print(f"   - Target audiences: {status_result['result']['target_audiences']}")
            print(f"   - Confidence: {status_result['result']['confidence_score']}")
            return True
        elif status_result["status"] == "failed":
            print(f"   ✗ Job failed: {status_result.get('error')}")
            return False

        time.sleep(1)

    print(f"   ✗ Timeout waiting for job completion")
    return False


def test_web_search_manual():
    """Test web search in manual mode."""
    print("\n" + "="*60)
    print("TEST: Web Search (Manual Mode)")
    print("="*60)

    payload = {
        "client_company_name": "Omada Health",
        "research_mode": "manual",
        "prompts": [
            "Research Omada Health's diabetes prevention program",
            "Find clinical outcomes and ROI data",
            "Identify target customer segments"
        ]
    }

    print(f"\n1. Initiating manual research...")
    response = requests.post(f"{BASE_URL}/research/web-search", json=payload)

    assert response.status_code == 202
    result = response.json()
    job_id = result["job_id"]

    print(f"   ✓ Job created: {job_id}")
    print(f"   Prompts: {len(payload['prompts'])}")

    # Wait for completion
    for _ in range(30):
        response = requests.get(f"{BASE_URL}/research/{job_id}")
        status_result = response.json()

        if status_result["status"] == "completed":
            print(f"   ✓ Manual research completed")
            return True
        elif status_result["status"] == "failed":
            print(f"   ✗ Failed: {status_result.get('error')}")
            return False

        time.sleep(1)

    return False


def test_document_analysis():
    """Test document analysis."""
    print("\n" + "="*60)
    print("TEST: Document Analysis")
    print("="*60)

    payload = {
        "document_ids": [
            "s3://triton-docs/client123/roi_sheet.pdf",
            "s3://triton-docs/client123/case_study.pdf"
        ],
        "additional_context": "Client focuses on diabetes management for health plans"
    }

    print(f"\n1. Initiating document analysis...")
    print(f"   Documents: {len(payload['document_ids'])}")
    response = requests.post(f"{BASE_URL}/research/document-analysis", json=payload)

    assert response.status_code == 202
    result = response.json()
    job_id = result["job_id"]

    print(f"   ✓ Job created: {job_id}")

    # Wait for completion
    for _ in range(30):
        response = requests.get(f"{BASE_URL}/research/{job_id}")
        status_result = response.json()

        if status_result["status"] == "completed":
            print(f"   ✓ Document analysis completed")
            print(f"\n2. Analysis Results:")
            print(f"   - Documents analyzed: {status_result['result']['documents_analyzed']}")
            print(f"   - Value props extracted: {len(status_result['result']['extracted_value_propositions'])}")
            print(f"   - Confidence: {status_result['result']['overall_confidence']}")
            return True
        elif status_result["status"] == "failed":
            print(f"   ✗ Failed: {status_result.get('error')}")
            return False

        time.sleep(1)

    return False


def test_list_jobs():
    """Test listing research jobs."""
    print("\n" + "="*60)
    print("TEST: List Research Jobs")
    print("="*60)

    response = requests.get(f"{BASE_URL}/research/")
    assert response.status_code == 200

    result = response.json()
    print(f"\n   Total jobs: {result['total']}")
    print(f"   Page: {result['page']}/{result['page_size']} per page")
    print(f"   Jobs returned: {len(result['jobs'])}")

    for job in result['jobs'][:3]:  # Show first 3
        print(f"   - {job['job_id']}: {job['status']} ({job['research_type']})")

    return True


def test_get_stats():
    """Test getting research statistics."""
    print("\n" + "="*60)
    print("TEST: Research Statistics")
    print("="*60)

    response = requests.get(f"{BASE_URL}/research/stats/summary")
    assert response.status_code == 200

    result = response.json()
    print(f"\n   Statistics:")
    print(f"   - Total jobs: {result['total_jobs']}")
    print(f"   - Web search: {result['web_search_jobs']}")
    print(f"   - Document analysis: {result['document_analysis_jobs']}")
    print(f"   - Completed: {result['completed_jobs']}")
    print(f"   - Failed: {result['failed_jobs']}")
    if result.get('success_rate'):
        print(f"   - Success rate: {result['success_rate']*100:.1f}%")
    if result.get('average_duration_seconds'):
        print(f"   - Avg duration: {result['average_duration_seconds']:.1f}s")

    return True


def test_validation():
    """Test research result validation."""
    print("\n" + "="*60)
    print("TEST: Result Validation")
    print("="*60)

    # Test valid result
    valid_result = {
        "searches_performed": 18,
        "queries": ["test query"],
        "company_overview": {
            "name": "Test Company",
            "description": "A test company for validation purposes",
            "target_markets": ["Health Plans"]
        },
        "value_propositions": [
            {
                "name": "Test Value Prop",
                "description": "A test value proposition for validation",
                "evidence_type": "explicit",
                "supporting_sources": ["https://example.com"],
                "confidence": "high"
            }
        ],
        "clinical_outcomes": [],
        "target_audiences": ["Health Plan"],
        "sources": ["https://example.com"],
        "research_mode": "autonomous",
        "confidence_score": 0.85,
        "missing_information": [],
        "assumptions_made": [],
        "research_timestamp": "2025-01-15T12:00:00Z"
    }

    payload = {
        "result_data": valid_result,
        "result_type": "web_search"
    }

    response = requests.post(f"{BASE_URL}/research/validate", json=payload)
    assert response.status_code == 200

    result = response.json()
    print(f"\n   Valid: {result['valid']}")
    print(f"   Errors: {len(result['errors'])}")
    print(f"   Warnings: {len(result['warnings'])}")
    print(f"   Confidence: {result.get('confidence_score')}")

    if result['warnings']:
        for warning in result['warnings']:
            print(f"   ⚠️  {warning}")

    return result['valid']


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" "*20 + "RESEARCH API TEST SUITE")
    print("="*70)
    print(f"\nBase URL: {BASE_URL}")
    print("Make sure the API server is running: uvicorn app:app --reload")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("\n✗ API server not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API server. Start it with:")
        print("   uvicorn app:app --reload")
        return

    print("✓ API server is running\n")

    # Run tests
    tests = [
        ("Web Search (Autonomous)", test_web_search_autonomous),
        ("Web Search (Manual)", test_web_search_manual),
        ("Document Analysis", test_document_analysis),
        ("List Jobs", test_list_jobs),
        ("Get Statistics", test_get_stats),
        ("Validation", test_validation),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ✗ Test failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

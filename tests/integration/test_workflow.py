#!/usr/bin/env python3
"""
Integration test for Mare-API → Triton workflow.

Tests the complete end-to-end flow:
1. Create client via Mare-API (proxies to Triton)
2. Create value proposition
3. Submit template generation job
4. Poll job status until completion
5. Retrieve generated templates
6. Verify data integrity

Usage:
    python tests/integration/test_workflow.py [--verbose] [--mare-api-url URL] [--triton-api-url URL]
"""

import argparse
import asyncio
import httpx
import json
import sys
import time
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class WorkflowTester:
    """Test harness for Mare-API → Triton integration."""

    def __init__(self, mare_api_url: str, triton_api_url: str, verbose: bool = False):
        self.mare_api_url = mare_api_url.rstrip('/')
        self.triton_api_url = triton_api_url.rstrip('/')
        self.verbose = verbose
        self.metrics = {}
        self.test_results = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding."""
        color_map = {
            "INFO": Colors.OKBLUE,
            "SUCCESS": Colors.OKGREEN,
            "WARNING": Colors.WARNING,
            "ERROR": Colors.FAIL,
            "HEADER": Colors.HEADER
        }
        color = color_map.get(level, "")
        print(f"{color}[{level}] {message}{Colors.ENDC}")

    def record_metric(self, name: str, value: float, unit: str = ""):
        """Record a performance metric."""
        self.metrics[name] = {"value": value, "unit": unit}
        if self.verbose:
            self.log(f"Metric: {name} = {value:.2f}{unit}", "INFO")

    def record_result(self, step: str, success: bool, duration: float, details: str = ""):
        """Record test step result."""
        self.test_results.append({
            "step": step,
            "success": success,
            "duration_ms": duration * 1000,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def test_health_checks(self) -> bool:
        """Test health endpoints for both services."""
        self.log("="*80, "HEADER")
        self.log("Step 1: Health Checks", "HEADER")
        self.log("="*80, "HEADER")

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test Mare-API health
            start = time.time()
            try:
                response = await client.get(f"{self.mare_api_url}/v1/triton/health")
                duration = time.time() - start
                self.record_metric("mare_api_health_check_time", duration, "s")

                if response.status_code == 200:
                    self.log(f"✓ Mare-API health check passed ({duration*1000:.0f}ms)", "SUCCESS")
                    self.record_result("mare_api_health", True, duration, str(response.json()))
                else:
                    self.log(f"✗ Mare-API health check failed: {response.status_code}", "ERROR")
                    self.record_result("mare_api_health", False, duration, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                duration = time.time() - start
                self.log(f"✗ Mare-API unreachable: {e}", "ERROR")
                self.record_result("mare_api_health", False, duration, str(e))
                return False

            # Test Triton API health
            start = time.time()
            try:
                response = await client.get(f"{self.triton_api_url}/health")
                duration = time.time() - start
                self.record_metric("triton_api_health_check_time", duration, "s")

                if response.status_code == 200:
                    self.log(f"✓ Triton API health check passed ({duration*1000:.0f}ms)", "SUCCESS")
                    self.record_result("triton_api_health", True, duration, str(response.json()))
                else:
                    self.log(f"✗ Triton API health check failed: {response.status_code}", "ERROR")
                    self.record_result("triton_api_health", False, duration, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                duration = time.time() - start
                self.log(f"✗ Triton API unreachable: {e}", "ERROR")
                self.record_result("triton_api_health", False, duration, str(e))
                return False

        return True

    async def create_client(self) -> Optional[str]:
        """Create a test client via Mare-API."""
        self.log("\n" + "="*80, "HEADER")
        self.log("Step 2: Create Client", "HEADER")
        self.log("="*80, "HEADER")

        client_data = {
            "name": f"Test Healthcare Corp {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "industry": "Healthcare",
            "meta_data": {
                "test": True,
                "test_run_id": datetime.utcnow().isoformat()
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            start = time.time()
            try:
                response = await client.post(
                    f"{self.mare_api_url}/v1/triton/clients",
                    json=client_data
                )
                duration = time.time() - start
                self.record_metric("client_creation_time", duration, "s")

                if response.status_code in [200, 201]:
                    data = response.json()
                    client_id = data.get("id")
                    self.log(f"✓ Client created: {client_id} ({duration*1000:.0f}ms)", "SUCCESS")
                    if self.verbose:
                        self.log(f"  Client data: {json.dumps(data, indent=2)}", "INFO")
                    self.record_result("create_client", True, duration, f"Client ID: {client_id}")
                    return client_id
                else:
                    self.log(f"✗ Client creation failed: {response.status_code}", "ERROR")
                    self.log(f"  Response: {response.text}", "ERROR")
                    self.record_result("create_client", False, duration, f"Status: {response.status_code}")
                    return None
            except Exception as e:
                duration = time.time() - start
                self.log(f"✗ Client creation error: {e}", "ERROR")
                self.record_result("create_client", False, duration, str(e))
                return None

    async def create_value_proposition(self, client_id: str) -> Optional[str]:
        """Create a value proposition for the client."""
        self.log("\n" + "="*80, "HEADER")
        self.log("Step 3: Create Value Proposition", "HEADER")
        self.log("="*80, "HEADER")

        vp_data = {
            "content": """Your organization faces critical challenges in healthcare delivery and operational efficiency.
            Our solution provides real-time dashboards that integrate clinical outcomes, financial metrics, and resource utilization.
            Gain actionable insights into patient care quality, cost optimization, and workforce productivity.
            Transform data into decisions with AI-powered analytics tailored for healthcare executives and managers.""",
            "is_active": True,
            "meta_data": {
                "test": True,
                "test_type": "integration_test"
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            start = time.time()
            try:
                response = await client.post(
                    f"{self.mare_api_url}/v1/triton/clients/{client_id}/value-propositions",
                    json=vp_data
                )
                duration = time.time() - start
                self.record_metric("value_proposition_creation_time", duration, "s")

                if response.status_code in [200, 201]:
                    data = response.json()
                    vp_id = data.get("id")
                    self.log(f"✓ Value proposition created: {vp_id} ({duration*1000:.0f}ms)", "SUCCESS")
                    self.record_result("create_value_proposition", True, duration, f"VP ID: {vp_id}")
                    return vp_id
                else:
                    self.log(f"✗ Value proposition creation failed: {response.status_code}", "ERROR")
                    self.log(f"  Response: {response.text}", "ERROR")
                    self.record_result("create_value_proposition", False, duration, f"Status: {response.status_code}")
                    return None
            except Exception as e:
                duration = time.time() - start
                self.log(f"✗ Value proposition creation error: {e}", "ERROR")
                self.record_result("create_value_proposition", False, duration, str(e))
                return None

    async def submit_generation_job(self, client_id: str) -> Optional[str]:
        """Submit a template generation job."""
        self.log("\n" + "="*80, "HEADER")
        self.log("Step 4: Submit Template Generation Job", "HEADER")
        self.log("="*80, "HEADER")

        async with httpx.AsyncClient(timeout=30.0) as client:
            start = time.time()
            try:
                response = await client.post(
                    f"{self.mare_api_url}/v1/triton/clients/{client_id}/generate-templates"
                )
                duration = time.time() - start
                self.record_metric("job_submission_time", duration, "s")

                if response.status_code in [200, 201, 202]:
                    data = response.json()
                    job_id = data.get("id") or data.get("job_id")
                    self.log(f"✓ Job submitted: {job_id} ({duration*1000:.0f}ms)", "SUCCESS")
                    self.log(f"  Status: {data.get('status')}", "INFO")
                    self.record_result("submit_generation_job", True, duration, f"Job ID: {job_id}")
                    return job_id
                else:
                    self.log(f"✗ Job submission failed: {response.status_code}", "ERROR")
                    self.log(f"  Response: {response.text}", "ERROR")
                    self.record_result("submit_generation_job", False, duration, f"Status: {response.status_code}")
                    return None
            except Exception as e:
                duration = time.time() - start
                self.log(f"✗ Job submission error: {e}", "ERROR")
                self.record_result("submit_generation_job", False, duration, str(e))
                return None

    async def wait_for_job_completion(self, job_id: str, max_wait: int = 300, poll_interval: int = 5) -> Optional[Dict]:
        """Poll job status until completion or timeout."""
        self.log("\n" + "="*80, "HEADER")
        self.log("Step 5: Wait for Job Completion", "HEADER")
        self.log("="*80, "HEADER")

        start_time = time.time()
        elapsed = 0
        poll_count = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            while elapsed < max_wait:
                poll_count += 1
                try:
                    response = await client.get(
                        f"{self.mare_api_url}/v1/triton/jobs/{job_id}"
                    )

                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        elapsed = time.time() - start_time

                        self.log(f"  Poll #{poll_count}: Status={status}, Elapsed={elapsed:.0f}s", "INFO")

                        if status == "completed":
                            self.record_metric("job_completion_time", elapsed, "s")
                            self.record_metric("job_poll_count", poll_count, "")
                            self.log(f"✓ Job completed successfully ({elapsed:.0f}s, {poll_count} polls)", "SUCCESS")
                            self.record_result("wait_for_completion", True, elapsed, "Job completed")
                            return data
                        elif status == "failed":
                            self.log(f"✗ Job failed: {data.get('error_message')}", "ERROR")
                            self.record_result("wait_for_completion", False, elapsed, f"Job failed: {data.get('error_message')}")
                            return data
                        elif status == "cancelled":
                            self.log(f"✗ Job was cancelled", "ERROR")
                            self.record_result("wait_for_completion", False, elapsed, "Job cancelled")
                            return data

                        # Still pending or running, wait and poll again
                        await asyncio.sleep(poll_interval)
                        elapsed = time.time() - start_time
                    else:
                        self.log(f"✗ Failed to get job status: {response.status_code}", "ERROR")
                        await asyncio.sleep(poll_interval)
                        elapsed = time.time() - start_time

                except Exception as e:
                    self.log(f"⚠ Error polling job status: {e}", "WARNING")
                    await asyncio.sleep(poll_interval)
                    elapsed = time.time() - start_time

            # Timeout
            self.log(f"✗ Job did not complete within {max_wait}s", "ERROR")
            self.record_result("wait_for_completion", False, elapsed, f"Timeout after {max_wait}s")
            return None

    async def retrieve_templates(self, client_id: str) -> Optional[list]:
        """Retrieve generated templates."""
        self.log("\n" + "="*80, "HEADER")
        self.log("Step 6: Retrieve Generated Templates", "HEADER")
        self.log("="*80, "HEADER")

        async with httpx.AsyncClient(timeout=30.0) as client:
            start = time.time()
            try:
                response = await client.get(
                    f"{self.mare_api_url}/v1/triton/templates?client_id={client_id}"
                )
                duration = time.time() - start
                self.record_metric("template_retrieval_time", duration, "s")

                if response.status_code == 200:
                    data = response.json()
                    templates = data.get("templates", [])
                    template_count = len(templates)

                    self.log(f"✓ Retrieved {template_count} templates ({duration*1000:.0f}ms)", "SUCCESS")
                    self.record_metric("templates_generated", template_count, "")
                    self.record_result("retrieve_templates", True, duration, f"Count: {template_count}")

                    if self.verbose and templates:
                        for i, template in enumerate(templates[:3], 1):  # Show first 3
                            self.log(f"  Template {i}: {template.get('name')}", "INFO")
                            self.log(f"    Category: {template.get('category')}", "INFO")
                            self.log(f"    Audience: {template.get('target_audience')}", "INFO")
                            self.log(f"    Widgets: {template.get('widget_count', 0)}", "INFO")

                    return templates
                else:
                    self.log(f"✗ Failed to retrieve templates: {response.status_code}", "ERROR")
                    self.record_result("retrieve_templates", False, duration, f"Status: {response.status_code}")
                    return None
            except Exception as e:
                duration = time.time() - start
                self.log(f"✗ Template retrieval error: {e}", "ERROR")
                self.record_result("retrieve_templates", False, duration, str(e))
                return None

    async def run_full_workflow(self) -> bool:
        """Run the complete integration test workflow."""
        self.log(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}", "HEADER")
        self.log(f"{Colors.BOLD}Triton + Mare-API Integration Test{Colors.ENDC}", "HEADER")
        self.log(f"{Colors.BOLD}{'='*80}{Colors.ENDC}", "HEADER")
        self.log(f"Mare-API: {self.mare_api_url}", "INFO")
        self.log(f"Triton API: {self.triton_api_url}", "INFO")
        self.log(f"Start time: {datetime.utcnow().isoformat()}", "INFO")

        overall_start = time.time()

        # Step 1: Health checks
        if not await self.test_health_checks():
            self.log("\n✗ Health checks failed, aborting test", "ERROR")
            return False

        # Step 2: Create client
        client_id = await self.create_client()
        if not client_id:
            self.log("\n✗ Client creation failed, aborting test", "ERROR")
            return False

        # Step 3: Create value proposition
        vp_id = await self.create_value_proposition(client_id)
        if not vp_id:
            self.log("\n✗ Value proposition creation failed, aborting test", "ERROR")
            return False

        # Step 4: Submit generation job
        job_id = await self.submit_generation_job(client_id)
        if not job_id:
            self.log("\n✗ Job submission failed, aborting test", "ERROR")
            return False

        # Step 5: Wait for completion
        final_status = await self.wait_for_job_completion(job_id, max_wait=300, poll_interval=5)
        if not final_status or final_status.get("status") != "completed":
            self.log("\n✗ Job did not complete successfully", "ERROR")
            return False

        # Step 6: Retrieve templates
        templates = await self.retrieve_templates(client_id)
        if not templates:
            self.log("\n✗ Failed to retrieve templates", "ERROR")
            return False

        # Calculate total time
        total_duration = time.time() - overall_start
        self.record_metric("total_workflow_time", total_duration, "s")

        # Print summary
        self.print_summary(total_duration)

        return True

    def print_summary(self, total_duration: float):
        """Print test summary."""
        self.log(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}", "HEADER")
        self.log(f"{Colors.BOLD}Test Summary{Colors.ENDC}", "HEADER")
        self.log(f"{Colors.BOLD}{'='*80}{Colors.ENDC}", "HEADER")

        # Count successes and failures
        successes = sum(1 for r in self.test_results if r["success"])
        failures = sum(1 for r in self.test_results if not r["success"])

        self.log(f"Total Steps: {len(self.test_results)}", "INFO")
        self.log(f"Successes: {successes}", "SUCCESS")
        self.log(f"Failures: {failures}", "ERROR" if failures > 0 else "INFO")
        self.log(f"Total Duration: {total_duration:.2f}s", "INFO")

        # Print key metrics
        self.log(f"\n{Colors.BOLD}Key Metrics:{Colors.ENDC}", "HEADER")
        for name, data in sorted(self.metrics.items()):
            value = data["value"]
            unit = data["unit"]
            if isinstance(value, float):
                self.log(f"  {name}: {value:.2f}{unit}", "INFO")
            else:
                self.log(f"  {name}: {value}{unit}", "INFO")

        # Save results to file
        self.save_results()

    def save_results(self):
        """Save test results to JSON file."""
        results = {
            "test_run": {
                "timestamp": datetime.utcnow().isoformat(),
                "mare_api_url": self.mare_api_url,
                "triton_api_url": self.triton_api_url,
            },
            "metrics": self.metrics,
            "steps": self.test_results
        }

        filename = f"test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        self.log(f"\n✓ Results saved to: {filename}", "SUCCESS")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Triton + Mare-API integration workflow")
    parser.add_argument("--mare-api-url", default="http://localhost:16000",
                        help="Mare-API base URL (default: http://localhost:16000)")
    parser.add_argument("--triton-api-url", default="http://localhost:8000",
                        help="Triton API base URL (default: http://localhost:8000)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")

    args = parser.parse_args()

    tester = WorkflowTester(
        mare_api_url=args.mare_api_url,
        triton_api_url=args.triton_api_url,
        verbose=args.verbose
    )

    try:
        success = await tester.run_full_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

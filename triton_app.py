"""Triton Template Generation Prototype

This application demonstrates:
- Single-purpose agent for dashboard template generation
- Structured output with Pydantic validation
- Automatic retry on validation failure
- Agent contains all business logic in instructions
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.models.model_factory import get_default_model
from core.config.settings import config
from core.monitoring.logger import get_logger
from agents.template_generator_agent import create_template_generator_with_retry
from core.models.template_models import TemplateGenerationResult

logger = get_logger(__name__)


def main():
    """Run template generation prototype."""
    print("=" * 80)
    print("Triton: Dashboard Template Generation Prototype")
    print("=" * 80)
    print()

    # Configuration
    client_name = "Livongo Health"
    industry = "Diabetes Management"
    target_audiences = ["Health Plan", "Broker", "Medical Management"]

    print("Configuration:")
    print(f"  Client: {client_name}")
    print(f"  Industry: {industry}")
    print(f"  Target Audiences: {', '.join(target_audiences)}")
    print()

    # Step 1: Create the agent
    print("Step 1: Creating Template Generator Agent...")
    print("  - Comprehensive instructions (~300+ lines)")
    print("  - Structured output with Pydantic validation")
    print("  - Automatic retry on validation failure (max 3 attempts)")
    print()

    try:
        model = get_default_model(max_tokens=16000)
        print(f"  Model: {model}")

        agent = create_template_generator_with_retry(
            name="TemplateGeneratorAgent",
            model=model,
            max_retries=3
        )
        print(f"  Agent created: {agent.name}")
        print()

    except Exception as e:
        print(f"Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 2: Load example value proposition
    print("Step 2: Loading Example Value Proposition...")
    print()

    # For prototype, use a simplified value proposition
    # In production, this would come from PostgreSQL
    value_proposition = {
        "executive_value_proposition": {
            "core_value_statement": (
                "Livongo's AI-powered diabetes management platform delivers measurable "
                "clinical outcomes and substantial cost savings through personalized member "
                "engagement, real-time coaching, and data-driven interventions."
            ),
            "primary_impact_areas": [
                "Clinical Outcomes Improvement",
                "Healthcare Cost Reduction",
                "Member Engagement & Satisfaction"
            ]
        },
        "value_proposition_priorities": [
            {
                "priority_id": "vp_1",
                "priority_name": "Reduce Diabetes-Related Costs",
                "description": "Lower total cost of care for diabetic members through preventive interventions",
                "typical_savings_range": "$150-$300 PMPM",
                "time_to_impact": "12-18 months",
                "key_metrics": [
                    "ED visit reduction",
                    "Hospitalization avoidance",
                    "Medication adherence improvement",
                    "Complication prevention"
                ]
            },
            {
                "priority_id": "vp_2",
                "priority_name": "Improve Clinical Outcomes",
                "description": "Achieve better HbA1c control and quality measure scores",
                "typical_savings_range": "N/A",
                "time_to_impact": "6-12 months",
                "key_metrics": [
                    "HbA1c reduction",
                    "% members with controlled HbA1c",
                    "HEDIS diabetes measures",
                    "Complication rates"
                ]
            },
            {
                "priority_id": "vp_3",
                "priority_name": "Enhance Member Engagement",
                "description": "Drive program adoption and sustained member participation",
                "typical_savings_range": "N/A",
                "time_to_impact": "3-6 months",
                "key_metrics": [
                    "Enrollment rates",
                    "Active engagement rates",
                    "App usage metrics",
                    "Member satisfaction scores"
                ]
            }
        ],
        "clinical_outcomes": {
            "primary_outcomes": [
                {"outcome": "HbA1c reduction", "typical_improvement": "0.5-1.0% reduction"},
                {"outcome": "Complication rate reduction", "typical_improvement": "15-25% reduction"},
                {"outcome": "HEDIS measure improvement", "typical_improvement": "10-15 percentage points"}
            ]
        },
        "roi_opportunities": {
            "tier_1_highest_impact": [
                {
                    "opportunity_name": "Emergency Department Visit Reduction",
                    "annual_savings_per_member": "$250-$400",
                    "confidence_level": "HIGH"
                },
                {
                    "opportunity_name": "Hospital Readmission Prevention",
                    "annual_savings_per_member": "$500-$800",
                    "confidence_level": "HIGH"
                },
                {
                    "opportunity_name": "Medication Adherence Improvement",
                    "annual_savings_per_member": "$100-$200",
                    "confidence_level": "MEDIUM"
                }
            ]
        }
    }

    print("Value Proposition loaded:")
    print(f"  - Core value statement: {len(value_proposition['executive_value_proposition']['core_value_statement'])} chars")
    print(f"  - Priorities: {len(value_proposition['value_proposition_priorities'])}")
    print(f"  - Primary outcomes: {len(value_proposition['clinical_outcomes']['primary_outcomes'])}")
    print()

    # Step 3: Create the task
    print("Step 3: Creating Generation Task...")
    print()

    task = f"""
Generate 5-10 dashboard template variations for the following client value proposition:

**Client Information:**
- Name: {client_name}
- Industry: {industry}
- Target Audiences: {', '.join(target_audiences)}

**Value Proposition:**
{json.dumps(value_proposition, indent=2)}

**Your Task:**
1. Analyze the value proposition to identify key metrics and themes
2. Generate 5-10 dashboard template variations across all categories
3. Ensure templates cover all target audiences: {', '.join(target_audiences)}
4. Each template should have 6-12 widgets with appropriate types and layouts
5. Use visual styles appropriate for each category
6. Follow all constraints strictly (widget types, grid layout, etc.)

Return a complete TemplateGenerationResult JSON with all templates and metadata.
"""

    print("Task created")
    print()

    # Step 4: Run the agent
    print("Step 4: Running Agent...")
    print("=" * 80)
    print()

    start_time = time.time()

    try:
        print("  Running agent (with automatic retry on validation failure)...")
        print()

        result: TemplateGenerationResult = agent.run(
            task,
            target_audiences=target_audiences
        )

        # Extract content if wrapped
        if hasattr(result, 'content'):
            result = result.content

        end_time = time.time()
        elapsed = end_time - start_time

        print()
        print("=" * 80)
        print("✅ Template Generation Complete")
        print("=" * 80)
        print()

        # Update metadata
        result.metadata.generation_time_seconds = round(elapsed, 2)
        result.metadata.client_name = client_name
        result.metadata.industry = industry
        result.metadata.total_templates = len(result.templates)

        print("Summary:")
        print("=" * 80)
        print(f"  Total Templates Generated: {len(result.templates)}")
        print(f"  Generation Time: {elapsed:.2f} seconds")
        print(f"  Validation Passed: {result.metadata.validation_passed}")
        print()

        print("Templates by Category:")
        from collections import Counter
        categories = Counter(t.category for t in result.templates)
        for category, count in categories.items():
            print(f"  - {category}: {count}")
        print()

        print("Templates by Audience:")
        audiences = Counter(t.targetAudience for t in result.templates)
        for audience, count in audiences.items():
            print(f"  - {audience}: {count}")
        print()

        # Check coverage
        if result.unmapped_categories:
            print(f"⚠️  Missing categories: {', '.join(result.unmapped_categories)}")
        if result.unmapped_audiences:
            print(f"⚠️  Missing audiences: {', '.join(result.unmapped_audiences)}")

        # Save result to file
        output_file = "results/templates_result.json"
        os.makedirs("results", exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(result.model_dump(), f, indent=2, default=str)

        print(f"✅ Result saved to: {output_file}")
        print()

        # Show template details
        print("Generated Templates:")
        print("=" * 80)
        for i, template in enumerate(result.templates, 1):
            print(f"\n{i}. {template.name}")
            print(f"   Category: {template.category}")
            print(f"   Audience: {template.targetAudience}")
            print(f"   Widgets: {len(template.widgets)}")
            print(f"   Key Features: {', '.join(template.keyFeatures[:2])}...")
            print(f"   Colors: {template.visualStyle.primaryColor} / {template.visualStyle.accentColor}")

        print()
        print("=" * 80)

        return result

    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  Triton: Dashboard Template Generation Prototype".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Run prototype
    result = main()

    if result:
        print()
        print("Next Steps:")
        print("  1. Review generated templates in: results/templates_result.json")
        print("  2. Test with different value propositions")
        print("  3. Integrate with Celery for async processing")
        print("  4. Add PostgreSQL storage")
        print("  5. Create REST API endpoints")
        print()

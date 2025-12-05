"""
Healthcare Metrics Library

Provides a catalog of common healthcare metrics that can be referenced by the
template generation agent. Each metric includes SQL expression, data type,
formatting rules, and required tables.

The LLM can reference these metrics using 'metric_ref' or create custom metrics
with custom 'expression' values.
"""

from typing import Dict, List, Any, Literal

# Metric Categories
METRIC_CATEGORIES = {
    "clinical": "Clinical Outcomes",
    "financial": "Financial & ROI",
    "operational": "Operational Efficiency",
    "engagement": "Member Engagement",
    "quality": "Quality Measures"
}


# =============================================================================
# METRICS LIBRARY
# =============================================================================

METRICS_LIBRARY: Dict[str, Dict[str, Any]] = {

    # =========================================================================
    # CLINICAL METRICS
    # =========================================================================

    "member_count": {
        "name": "Member Count",
        "expression": "COUNT(DISTINCT member_id)",
        "data_type": "count",
        "format": "0,0",
        "category": "clinical",
        "description": "Total unique members in the program",
        "required_tables": ["enrollments"],
        "common_filters": ["program_status = 'active'"]
    },

    "enrolled_member_count": {
        "name": "Enrolled Member Count",
        "expression": "COUNT(DISTINCT enrollments.member_id)",
        "data_type": "count",
        "format": "0,0",
        "category": "clinical",
        "description": "Members actively enrolled",
        "required_tables": ["enrollments"],
        "common_filters": ["program_status = 'active'"]
    },

    "avg_hba1c": {
        "name": "Average HbA1c",
        "expression": "AVG(current_hba1c)",
        "data_type": "number",
        "format": "0.0",
        "category": "clinical",
        "description": "Average current HbA1c level",
        "required_tables": ["clinical_outcomes"],
        "unit": "%"
    },

    "avg_hba1c_reduction": {
        "name": "Average HbA1c Reduction",
        "expression": "AVG(baseline_hba1c - current_hba1c)",
        "data_type": "number",
        "format": "0.0",
        "category": "clinical",
        "description": "Average reduction in HbA1c from baseline",
        "required_tables": ["clinical_outcomes"],
        "unit": "%"
    },

    "baseline_hba1c": {
        "name": "Baseline HbA1c",
        "expression": "AVG(baseline_hba1c)",
        "data_type": "number",
        "format": "0.0",
        "category": "clinical",
        "description": "Average HbA1c at program start",
        "required_tables": ["clinical_outcomes"],
        "unit": "%"
    },

    "controlled_members": {
        "name": "Controlled Members",
        "expression": "COUNT(DISTINCT CASE WHEN current_hba1c < 7.0 THEN member_id END)",
        "data_type": "count",
        "format": "0,0",
        "category": "clinical",
        "description": "Members with HbA1c under control (< 7%)",
        "required_tables": ["clinical_outcomes"]
    },

    "control_rate": {
        "name": "Control Rate",
        "expression": "(COUNT(DISTINCT CASE WHEN current_hba1c < 7.0 THEN member_id END) / COUNT(DISTINCT member_id) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "clinical",
        "description": "Percentage of members with controlled HbA1c",
        "required_tables": ["clinical_outcomes"]
    },

    "complication_rate": {
        "name": "Complication Rate",
        "expression": "(COUNT(complications) / COUNT(DISTINCT member_id) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "clinical",
        "description": "Rate of diabetes complications",
        "required_tables": ["clinical_outcomes", "complications"]
    },

    # =========================================================================
    # FINANCIAL METRICS
    # =========================================================================

    "total_savings": {
        "name": "Total Cost Savings",
        "expression": "SUM(avoided_costs)",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Cumulative cost savings from program",
        "required_tables": ["financial_outcomes"]
    },

    "total_costs": {
        "name": "Total Program Costs",
        "expression": "SUM(program_costs)",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Total program operational costs",
        "required_tables": ["financial_outcomes"]
    },

    "program_roi": {
        "name": "Program ROI",
        "expression": "(SUM(avoided_costs) / SUM(program_costs))",
        "data_type": "number",
        "format": "0.0x",
        "category": "financial",
        "description": "Return on investment ratio",
        "required_tables": ["financial_outcomes"]
    },

    "net_savings": {
        "name": "Net Savings",
        "expression": "(SUM(avoided_costs) - SUM(program_costs))",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Net savings after program costs",
        "required_tables": ["financial_outcomes"]
    },

    "pmpm_cost": {
        "name": "Per Member Per Month Cost",
        "expression": "(SUM(total_costs) / COUNT(DISTINCT member_id) / 12)",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Average monthly cost per member",
        "required_tables": ["financial_outcomes", "enrollments"]
    },

    "pmpm_savings": {
        "name": "Per Member Per Month Savings",
        "expression": "(SUM(avoided_costs) / COUNT(DISTINCT member_id) / 12)",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Average monthly savings per member",
        "required_tables": ["financial_outcomes", "enrollments"]
    },

    "hospitalization_savings": {
        "name": "Hospitalization Cost Savings",
        "expression": "SUM(CASE WHEN cost_category = 'hospitalization' THEN avoided_costs ELSE 0 END)",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Savings from avoided hospitalizations",
        "required_tables": ["financial_outcomes"]
    },

    "er_savings": {
        "name": "Emergency Room Savings",
        "expression": "SUM(CASE WHEN cost_category = 'er' THEN avoided_costs ELSE 0 END)",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Savings from avoided ER visits",
        "required_tables": ["financial_outcomes"]
    },

    "medication_savings": {
        "name": "Medication Cost Savings",
        "expression": "SUM(CASE WHEN cost_category = 'medication' THEN avoided_costs ELSE 0 END)",
        "data_type": "currency",
        "format": "$0,0",
        "category": "financial",
        "description": "Savings from medication optimization",
        "required_tables": ["financial_outcomes"]
    },

    # =========================================================================
    # OPERATIONAL METRICS
    # =========================================================================

    "ed_visits": {
        "name": "Emergency Department Visits",
        "expression": "SUM(ed_visits)",
        "data_type": "count",
        "format": "0,0",
        "category": "operational",
        "description": "Total ED visits",
        "required_tables": ["utilization"]
    },

    "ed_visit_rate": {
        "name": "ED Visit Rate per 1000",
        "expression": "(SUM(ed_visits) / COUNT(DISTINCT member_id) * 1000)",
        "data_type": "number",
        "format": "0.0",
        "category": "operational",
        "description": "ED visits per 1000 members",
        "required_tables": ["utilization", "enrollments"]
    },

    "hospitalizations": {
        "name": "Hospitalizations",
        "expression": "SUM(hospitalizations)",
        "data_type": "count",
        "format": "0,0",
        "category": "operational",
        "description": "Total inpatient admissions",
        "required_tables": ["utilization"]
    },

    "hospitalization_rate": {
        "name": "Hospitalization Rate per 1000",
        "expression": "(SUM(hospitalizations) / COUNT(DISTINCT member_id) * 1000)",
        "data_type": "number",
        "format": "0.0",
        "category": "operational",
        "description": "Hospitalizations per 1000 members",
        "required_tables": ["utilization", "enrollments"]
    },

    "readmission_rate": {
        "name": "30-Day Readmission Rate",
        "expression": "(SUM(readmissions_30d) / SUM(hospitalizations) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "operational",
        "description": "Percentage of 30-day readmissions",
        "required_tables": ["utilization"]
    },

    "avg_length_of_stay": {
        "name": "Average Length of Stay",
        "expression": "AVG(length_of_stay_days)",
        "data_type": "number",
        "format": "0.0",
        "category": "operational",
        "description": "Average hospital stay in days",
        "required_tables": ["utilization"]
    },

    # =========================================================================
    # ENGAGEMENT METRICS
    # =========================================================================

    "engagement_rate": {
        "name": "Member Engagement Rate",
        "expression": "(COUNT(DISTINCT CASE WHEN is_engaged = true THEN member_id END) / COUNT(DISTINCT member_id) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "engagement",
        "description": "Percentage of actively engaged members",
        "required_tables": ["member_engagement"]
    },

    "active_members": {
        "name": "Active Members",
        "expression": "COUNT(DISTINCT CASE WHEN is_engaged = true THEN member_id END)",
        "data_type": "count",
        "format": "0,0",
        "category": "engagement",
        "description": "Members actively using program features",
        "required_tables": ["member_engagement"]
    },

    "retention_rate": {
        "name": "Retention Rate",
        "expression": "(COUNT(DISTINCT CASE WHEN program_status = 'active' THEN member_id END) / COUNT(DISTINCT member_id) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "engagement",
        "description": "Member retention rate",
        "required_tables": ["enrollments"]
    },

    "avg_app_logins": {
        "name": "Average App Logins per Member",
        "expression": "AVG(app_login_count)",
        "data_type": "number",
        "format": "0.0",
        "category": "engagement",
        "description": "Average number of app logins",
        "required_tables": ["member_engagement"]
    },

    "coaching_sessions": {
        "name": "Total Coaching Sessions",
        "expression": "SUM(coaching_session_count)",
        "data_type": "count",
        "format": "0,0",
        "category": "engagement",
        "description": "Total health coaching sessions completed",
        "required_tables": ["member_engagement"]
    },

    # =========================================================================
    # QUALITY MEASURES
    # =========================================================================

    "hedis_diabetes_control": {
        "name": "HEDIS Diabetes Control Rate",
        "expression": "(COUNT(DISTINCT CASE WHEN current_hba1c < 8.0 THEN member_id END) / COUNT(DISTINCT member_id) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "quality",
        "description": "HEDIS measure: HbA1c < 8%",
        "required_tables": ["clinical_outcomes"]
    },

    "bp_control_rate": {
        "name": "Blood Pressure Control Rate",
        "expression": "(COUNT(DISTINCT CASE WHEN systolic_bp < 140 AND diastolic_bp < 90 THEN member_id END) / COUNT(DISTINCT member_id) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "quality",
        "description": "Members with controlled blood pressure",
        "required_tables": ["clinical_outcomes"]
    },

    "care_gap_closure": {
        "name": "Care Gap Closure Rate",
        "expression": "(COUNT(closed_gaps) / COUNT(total_gaps) * 100)",
        "data_type": "percentage",
        "format": "0.0",
        "category": "quality",
        "description": "Percentage of care gaps closed",
        "required_tables": ["quality_measures"]
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_metric(metric_ref: str) -> Dict[str, Any]:
    """
    Get metric definition by reference key.

    Args:
        metric_ref: Metric reference key (e.g., 'member_count')

    Returns:
        Dict with metric definition

    Raises:
        KeyError: If metric reference not found
    """
    if metric_ref not in METRICS_LIBRARY:
        raise KeyError(f"Metric '{metric_ref}' not found in library. Available metrics: {list(METRICS_LIBRARY.keys())}")

    return METRICS_LIBRARY[metric_ref]


def get_metrics_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """
    Get all metrics for a specific category.

    Args:
        category: Metric category ('clinical', 'financial', 'operational', 'engagement', 'quality')

    Returns:
        Dict of metrics in that category
    """
    return {
        key: value
        for key, value in METRICS_LIBRARY.items()
        if value.get("category") == category
    }


def list_available_metrics() -> List[str]:
    """Return list of all available metric reference keys."""
    return sorted(METRICS_LIBRARY.keys())


def get_metric_categories() -> Dict[str, str]:
    """Return dict of metric categories with descriptions."""
    return METRIC_CATEGORIES


# =============================================================================
# EXPORT FOR LLM CONTEXT
# =============================================================================

def get_metrics_library_for_llm() -> str:
    """
    Generate formatted metrics library documentation for LLM context.

    Returns:
        Formatted string describing all available metrics
    """
    output = ["# Healthcare Metrics Library\n"]
    output.append("Reference these metrics using 'metric_ref' in data_requirements.metrics\n")
    output.append("Or create custom metrics with your own 'expression'\n\n")

    for category_key, category_name in METRIC_CATEGORIES.items():
        metrics = get_metrics_by_category(category_key)
        if not metrics:
            continue

        output.append(f"## {category_name}\n")

        for ref_key, metric in metrics.items():
            output.append(f"### {ref_key}")
            output.append(f"- **Name:** {metric['name']}")
            output.append(f"- **Expression:** `{metric['expression']}`")
            output.append(f"- **Data Type:** {metric['data_type']}")
            output.append(f"- **Format:** {metric['format']}")
            if metric.get('unit'):
                output.append(f"- **Unit:** {metric['unit']}")
            output.append(f"- **Description:** {metric['description']}")
            output.append(f"- **Tables:** {', '.join(metric['required_tables'])}")
            output.append("")

    return "\n".join(output)

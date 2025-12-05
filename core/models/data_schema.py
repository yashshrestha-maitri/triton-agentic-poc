"""
Data Schema Definition for Prospect Analytics

Defines the available tables and columns in the prospect data model.
This schema is provided to the LLM agent during template generation so it can:
1. Generate valid SQL expressions referencing actual tables/columns
2. Create appropriate data_requirements for each widget
3. Build queries that match the actual data structure

This schema represents the standardized data model for healthcare prospects.
"""

from typing import Dict, List, Any

# =============================================================================
# DATA SCHEMA DEFINITION
# =============================================================================

DATA_SCHEMA: Dict[str, Dict[str, Any]] = {

    # =========================================================================
    # ENROLLMENTS TABLE
    # =========================================================================
    "enrollments": {
        "description": "Program enrollment records for all members",
        "columns": {
            "member_id": {
                "type": "string",
                "description": "Unique member identifier",
                "primary_key": True
            },
            "program_id": {
                "type": "string",
                "description": "Program identifier (e.g., 'diabetes', 'hypertension')"
            },
            "program_status": {
                "type": "string",
                "description": "Current enrollment status",
                "values": ["active", "inactive", "completed", "cancelled"]
            },
            "enrollment_date": {
                "type": "date",
                "description": "Date member enrolled in program"
            },
            "termination_date": {
                "type": "date",
                "description": "Date member left program (NULL if active)",
                "nullable": True
            },
            "program_type": {
                "type": "string",
                "description": "Type of healthcare program",
                "values": ["diabetes", "hypertension", "heart_health", "weight_management"]
            },
            "enrollment_channel": {
                "type": "string",
                "description": "How member enrolled",
                "values": ["provider_referral", "self_enrollment", "outreach", "auto_enrollment"]
            }
        },
        "common_joins": ["clinical_outcomes ON enrollments.member_id = clinical_outcomes.member_id"],
        "typical_filters": [
            "program_status = 'active'",
            "program_type = 'diabetes'",
            "enrollment_date >= '2024-01-01'"
        ]
    },

    # =========================================================================
    # CLINICAL_OUTCOMES TABLE
    # =========================================================================
    "clinical_outcomes": {
        "description": "Clinical measurements and health outcomes for members",
        "columns": {
            "member_id": {
                "type": "string",
                "description": "Unique member identifier",
                "foreign_key": "enrollments.member_id"
            },
            "measurement_date": {
                "type": "date",
                "description": "Date of clinical measurement"
            },
            "baseline_hba1c": {
                "type": "number",
                "description": "HbA1c percentage at program start",
                "unit": "%",
                "range": [4.0, 14.0]
            },
            "current_hba1c": {
                "type": "number",
                "description": "Most recent HbA1c percentage",
                "unit": "%",
                "range": [4.0, 14.0]
            },
            "baseline_weight": {
                "type": "number",
                "description": "Weight in pounds at program start",
                "unit": "lbs"
            },
            "current_weight": {
                "type": "number",
                "description": "Most recent weight in pounds",
                "unit": "lbs"
            },
            "systolic_bp": {
                "type": "number",
                "description": "Systolic blood pressure",
                "unit": "mmHg",
                "range": [80, 200]
            },
            "diastolic_bp": {
                "type": "number",
                "description": "Diastolic blood pressure",
                "unit": "mmHg",
                "range": [40, 120]
            },
            "ldl_cholesterol": {
                "type": "number",
                "description": "LDL cholesterol level",
                "unit": "mg/dL",
                "range": [40, 300]
            },
            "bmi": {
                "type": "number",
                "description": "Body Mass Index",
                "range": [15, 60]
            },
            "has_complication": {
                "type": "boolean",
                "description": "Whether member has diabetes complications"
            },
            "complication_type": {
                "type": "string",
                "description": "Type of complication if present",
                "values": ["retinopathy", "nephropathy", "neuropathy", "cvd", "none"],
                "nullable": True
            }
        },
        "common_joins": ["enrollments ON clinical_outcomes.member_id = enrollments.member_id"],
        "typical_filters": [
            "measurement_date = (SELECT MAX(measurement_date) FROM clinical_outcomes WHERE member_id = clinical_outcomes.member_id)",
            "current_hba1c < 7.0",
            "has_complication = false"
        ]
    },

    # =========================================================================
    # FINANCIAL_OUTCOMES TABLE
    # =========================================================================
    "financial_outcomes": {
        "description": "Financial metrics including costs, savings, and ROI",
        "columns": {
            "member_id": {
                "type": "string",
                "description": "Unique member identifier",
                "foreign_key": "enrollments.member_id"
            },
            "period": {
                "type": "date",
                "description": "Month or period for financial data"
            },
            "program_costs": {
                "type": "currency",
                "description": "Direct program costs for this period",
                "unit": "USD"
            },
            "avoided_costs": {
                "type": "currency",
                "description": "Costs avoided through program interventions",
                "unit": "USD"
            },
            "total_healthcare_costs": {
                "type": "currency",
                "description": "Total healthcare costs for period",
                "unit": "USD"
            },
            "diabetes_related_costs": {
                "type": "currency",
                "description": "Costs specifically related to diabetes",
                "unit": "USD"
            },
            "cost_category": {
                "type": "string",
                "description": "Category of cost",
                "values": ["hospitalization", "er", "medication", "outpatient", "lab", "other"]
            },
            "baseline_costs": {
                "type": "currency",
                "description": "Healthcare costs before program enrollment",
                "unit": "USD"
            },
            "savings_category": {
                "type": "string",
                "description": "Type of savings achieved",
                "values": ["avoided_admission", "avoided_er", "medication_optimization", "complication_prevention"]
            }
        },
        "common_joins": ["enrollments ON financial_outcomes.member_id = enrollments.member_id"],
        "typical_filters": [
            "period >= '2024-01-01'",
            "avoided_costs > 0",
            "cost_category = 'hospitalization'"
        ],
        "aggregations": {
            "total_savings": "SUM(avoided_costs)",
            "total_program_costs": "SUM(program_costs)",
            "roi": "SUM(avoided_costs) / SUM(program_costs)",
            "net_savings": "SUM(avoided_costs) - SUM(program_costs)"
        }
    },

    # =========================================================================
    # UTILIZATION TABLE
    # =========================================================================
    "utilization": {
        "description": "Healthcare utilization metrics (ED visits, hospitalizations, etc.)",
        "columns": {
            "member_id": {
                "type": "string",
                "description": "Unique member identifier",
                "foreign_key": "enrollments.member_id"
            },
            "period": {
                "type": "date",
                "description": "Month or period for utilization data"
            },
            "ed_visits": {
                "type": "count",
                "description": "Number of emergency department visits"
            },
            "hospitalizations": {
                "type": "count",
                "description": "Number of inpatient admissions"
            },
            "readmissions_30d": {
                "type": "count",
                "description": "Number of 30-day readmissions"
            },
            "length_of_stay_days": {
                "type": "number",
                "description": "Average length of stay for hospitalizations",
                "unit": "days"
            },
            "outpatient_visits": {
                "type": "count",
                "description": "Number of outpatient visits"
            },
            "primary_care_visits": {
                "type": "count",
                "description": "Number of primary care visits"
            },
            "specialist_visits": {
                "type": "count",
                "description": "Number of specialist visits"
            },
            "lab_tests": {
                "type": "count",
                "description": "Number of laboratory tests"
            }
        },
        "common_joins": ["enrollments ON utilization.member_id = enrollments.member_id"],
        "typical_filters": [
            "period >= '2024-01-01'",
            "ed_visits > 0",
            "hospitalizations > 0"
        ],
        "aggregations": {
            "total_ed_visits": "SUM(ed_visits)",
            "ed_rate_per_1000": "SUM(ed_visits) / COUNT(DISTINCT member_id) * 1000",
            "total_hospitalizations": "SUM(hospitalizations)",
            "hospitalization_rate_per_1000": "SUM(hospitalizations) / COUNT(DISTINCT member_id) * 1000",
            "readmission_rate": "SUM(readmissions_30d) / SUM(hospitalizations) * 100"
        }
    },

    # =========================================================================
    # MEMBER_ENGAGEMENT TABLE
    # =========================================================================
    "member_engagement": {
        "description": "Member engagement and program participation metrics",
        "columns": {
            "member_id": {
                "type": "string",
                "description": "Unique member identifier",
                "foreign_key": "enrollments.member_id"
            },
            "period": {
                "type": "date",
                "description": "Month or period for engagement data"
            },
            "is_engaged": {
                "type": "boolean",
                "description": "Whether member is actively engaged this period"
            },
            "app_login_count": {
                "type": "count",
                "description": "Number of app logins this period"
            },
            "coaching_session_count": {
                "type": "count",
                "description": "Number of health coaching sessions attended"
            },
            "bg_reading_count": {
                "type": "count",
                "description": "Number of blood glucose readings logged"
            },
            "message_count": {
                "type": "count",
                "description": "Number of messages sent to care team"
            },
            "days_active": {
                "type": "count",
                "description": "Number of days with any engagement activity"
            },
            "content_views": {
                "type": "count",
                "description": "Number of educational content items viewed"
            },
            "last_activity_date": {
                "type": "date",
                "description": "Date of most recent engagement activity"
            }
        },
        "common_joins": ["enrollments ON member_engagement.member_id = enrollments.member_id"],
        "typical_filters": [
            "period >= '2024-01-01'",
            "is_engaged = true",
            "app_login_count > 0"
        ],
        "aggregations": {
            "engagement_rate": "(COUNT(DISTINCT CASE WHEN is_engaged = true THEN member_id END) / COUNT(DISTINCT member_id) * 100)",
            "avg_app_logins": "AVG(app_login_count)",
            "total_coaching_sessions": "SUM(coaching_session_count)",
            "avg_days_active": "AVG(days_active)"
        }
    },

    # =========================================================================
    # QUALITY_MEASURES TABLE
    # =========================================================================
    "quality_measures": {
        "description": "Quality measures and HEDIS scores",
        "columns": {
            "member_id": {
                "type": "string",
                "description": "Unique member identifier",
                "foreign_key": "enrollments.member_id"
            },
            "measure_year": {
                "type": "number",
                "description": "Year of quality measurement"
            },
            "hedis_diabetes_control": {
                "type": "boolean",
                "description": "Meets HEDIS diabetes control measure (HbA1c < 8%)"
            },
            "hedis_bp_control": {
                "type": "boolean",
                "description": "Meets HEDIS BP control measure"
            },
            "hedis_eye_exam": {
                "type": "boolean",
                "description": "Completed eye exam per HEDIS"
            },
            "hedis_kidney_test": {
                "type": "boolean",
                "description": "Completed kidney test per HEDIS"
            },
            "total_gaps": {
                "type": "count",
                "description": "Total number of care gaps identified"
            },
            "closed_gaps": {
                "type": "count",
                "description": "Number of care gaps closed"
            },
            "stars_rating_contribution": {
                "type": "number",
                "description": "Contribution to Stars rating",
                "range": [0, 5]
            }
        },
        "common_joins": ["enrollments ON quality_measures.member_id = enrollments.member_id"],
        "typical_filters": [
            "measure_year = 2024",
            "hedis_diabetes_control = true",
            "total_gaps > 0"
        ],
        "aggregations": {
            "hedis_control_rate": "(COUNT(CASE WHEN hedis_diabetes_control = true THEN 1 END) / COUNT(*) * 100)",
            "care_gap_closure_rate": "(SUM(closed_gaps) / SUM(total_gaps) * 100)",
            "avg_stars_contribution": "AVG(stars_rating_contribution)"
        }
    },

    # =========================================================================
    # COMPLICATIONS TABLE
    # =========================================================================
    "complications": {
        "description": "Diabetes complication events and dates",
        "columns": {
            "member_id": {
                "type": "string",
                "description": "Unique member identifier",
                "foreign_key": "enrollments.member_id"
            },
            "complication_date": {
                "type": "date",
                "description": "Date complication was diagnosed"
            },
            "complication_type": {
                "type": "string",
                "description": "Type of diabetes complication",
                "values": ["retinopathy", "nephropathy", "neuropathy", "cvd", "amputation", "dka"]
            },
            "severity": {
                "type": "string",
                "description": "Severity of complication",
                "values": ["mild", "moderate", "severe"]
            },
            "is_resolved": {
                "type": "boolean",
                "description": "Whether complication has been resolved"
            },
            "associated_cost": {
                "type": "currency",
                "description": "Healthcare costs associated with complication",
                "unit": "USD"
            }
        },
        "common_joins": ["enrollments ON complications.member_id = enrollments.member_id"],
        "typical_filters": [
            "complication_date >= '2024-01-01'",
            "complication_type = 'retinopathy'",
            "is_resolved = false"
        ],
        "aggregations": {
            "total_complications": "COUNT(*)",
            "complication_rate": "(COUNT(DISTINCT member_id) / (SELECT COUNT(*) FROM enrollments) * 100)",
            "avg_complication_cost": "AVG(associated_cost)"
        }
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    Get schema definition for a specific table.

    Args:
        table_name: Name of the table

    Returns:
        Dict with table schema

    Raises:
        KeyError: If table not found
    """
    if table_name not in DATA_SCHEMA:
        raise KeyError(f"Table '{table_name}' not found in schema. Available tables: {list(DATA_SCHEMA.keys())}")

    return DATA_SCHEMA[table_name]


def get_column_info(table_name: str, column_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific column."""
    table = get_table_schema(table_name)
    if column_name not in table["columns"]:
        raise KeyError(f"Column '{column_name}' not found in table '{table_name}'")

    return table["columns"][column_name]


def list_tables() -> List[str]:
    """Return list of all available table names."""
    return sorted(DATA_SCHEMA.keys())


def get_tables_with_column(column_name: str) -> List[str]:
    """Find all tables that have a specific column."""
    tables = []
    for table_name, table_def in DATA_SCHEMA.items():
        if column_name in table_def["columns"]:
            tables.append(table_name)
    return tables


# =============================================================================
# EXPORT FOR LLM CONTEXT
# =============================================================================

def get_data_schema_for_llm() -> str:
    """
    Generate formatted data schema documentation for LLM context.

    Returns:
        Formatted string describing all tables and columns
    """
    output = ["# Prospect Data Model Schema\n"]
    output.append("Use these tables and columns when writing SQL expressions in data_requirements.\n\n")

    for table_name, table_def in DATA_SCHEMA.items():
        output.append(f"## Table: {table_name}")
        output.append(f"**Description:** {table_def['description']}\n")

        output.append("### Columns:")
        for col_name, col_def in table_def["columns"].items():
            col_line = f"- **{col_name}** ({col_def['type']}): {col_def['description']}"
            if col_def.get("unit"):
                col_line += f" [{col_def['unit']}]"
            if col_def.get("values"):
                col_line += f"\n  - Values: {', '.join(col_def['values'])}"
            output.append(col_line)

        if table_def.get("common_joins"):
            output.append("\n### Common Joins:")
            for join in table_def["common_joins"]:
                output.append(f"- `{join}`")

        if table_def.get("typical_filters"):
            output.append("\n### Typical Filters:")
            for filter_example in table_def["typical_filters"]:
                output.append(f"- `{filter_example}`")

        if table_def.get("aggregations"):
            output.append("\n### Common Aggregations:")
            for agg_name, agg_expr in table_def["aggregations"].items():
                output.append(f"- **{agg_name}**: `{agg_expr}`")

        output.append("\n" + "-" * 80 + "\n")

    return "\n".join(output)

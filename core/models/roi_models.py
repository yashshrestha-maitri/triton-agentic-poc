"""
ROI Model Pydantic Models

This module defines the complete data models for ROI Model JSON generation.
These models support all 13 ROI model types (B1-B13) with comprehensive validation.

Model Structure:
- ROIModelJSON (root) contains 15 main components
- Each component has strict validation matching business rules
- Models support both model generation and real-time calculation phases

Usage:
    from core.models.roi_models import ROIModelJSON, validate_roi_model

    roi_model = ROIModelJSON(**data)
    validation = validate_roi_model(roi_model)
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS AND TYPE DEFINITIONS
# ============================================================================

class ModelTypeCode(str, Enum):
    """13 ROI Model Types"""
    B1 = "B1"  # Unit Price Optimization
    B2 = "B2"  # Site of Service Optimization
    B3 = "B3"  # Value-Based Care ROI
    B4 = "B4"  # Payment Integrity
    B5 = "B5"  # Prior Authorization ROI
    B6 = "B6"  # Case Management ROI
    B7 = "B7"  # Episode Optimization
    B8 = "B8"  # Pharmacy Optimization
    B9 = "B9"  # Network Steerage
    B10 = "B10"  # Utilization Management
    B11 = "B11"  # Quality Improvement ROI
    B12 = "B12"  # Population Health ROI
    B13 = "B13"  # Custom ROI Model


class MetricType(str, Enum):
    """Output metric types"""
    FINANCIAL = "financial"
    CLINICAL = "clinical"
    OPERATIONAL = "operational"
    QUALITY = "quality"


class ParameterType(str, Enum):
    """Parameter types for configurable parameters"""
    TIME = "time"
    RATE = "rate"
    COST = "cost"
    THRESHOLD = "threshold"
    PERCENTAGE = "percentage"
    COUNT = "count"


# ============================================================================
# COMPONENT 1: MODEL METADATA
# ============================================================================

class ROIModelMetadata(BaseModel):
    """Metadata about the ROI model"""
    model_type_code: ModelTypeCode = Field(..., description="ROI model type (B1-B13)")
    model_type_name: str = Field(..., description="Human-readable model type name")
    client_name: str = Field(..., min_length=1, description="Client organization name")
    source_document: Optional[str] = Field(None, description="Source document S3 path or URL")
    created_at: datetime = Field(default_factory=datetime.now, description="Model creation timestamp")
    version: str = Field(default="1.0.0", description="Model version")
    status: Literal["draft", "validated", "production"] = Field(default="draft", description="Model status")

    @field_validator('client_name')
    @classmethod
    def validate_client_name(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Client name cannot be empty")
        return v.strip()


# ============================================================================
# COMPONENT 2: EXECUTIVE SUMMARY
# ============================================================================

class ExecutiveSummary(BaseModel):
    """High-level summary of ROI model"""
    problem_statement: str = Field(..., min_length=50, description="Problem being addressed")
    solution_approach: str = Field(..., min_length=50, description="Solution methodology")
    expected_impact: str = Field(..., min_length=50, description="Expected financial/clinical impact")
    key_assumptions: List[str] = Field(..., min_items=1, description="Critical assumptions")
    target_population_size: Optional[int] = Field(None, ge=0, description="Estimated cohort size")
    estimated_annual_savings: Optional[float] = Field(None, ge=0, description="Projected annual savings")

    @field_validator('key_assumptions')
    @classmethod
    def validate_assumptions(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("At least one key assumption required")
        return [a.strip() for a in v if a.strip()]


# ============================================================================
# COMPONENT 3: DATA REQUIREMENTS
# ============================================================================

class DataSource(BaseModel):
    """Individual data source specification"""
    source_name: str = Field(..., description="Data source name (e.g., medical_claims)")
    source_type: Literal["claims", "enrollment", "clinical", "pharmacy", "external"] = Field(..., description="Type of data source")
    required_fields: List[str] = Field(..., min_items=1, description="Required fields from this source")
    date_range_required: bool = Field(default=True, description="Whether date range filtering needed")
    join_keys: Optional[List[str]] = Field(None, description="Keys for joining to other sources")


class DataRequirements(BaseModel):
    """Complete data requirements for ROI model"""
    data_sources: List[DataSource] = Field(..., min_items=1, description="Required data sources")
    minimum_lookback_months: int = Field(..., ge=1, le=60, description="Minimum historical data required (months)")
    data_quality_requirements: List[str] = Field(default_factory=list, description="Data quality criteria")

    @field_validator('data_sources')
    @classmethod
    def validate_data_sources(cls, v: List[DataSource]) -> List[DataSource]:
        if not v or len(v) == 0:
            raise ValueError("At least one data source required")
        return v


# ============================================================================
# COMPONENT 4: EPISODE DEFINITION (for episode-based models)
# ============================================================================

class EpisodeDefinition(BaseModel):
    """Episode definition for episode-based ROI models (B7, etc.)"""
    episode_type: str = Field(..., description="Type of episode (e.g., MSK, Maternity)")
    trigger_events: List[str] = Field(..., min_items=1, description="Events that trigger episode start")
    episode_window_days: int = Field(..., ge=1, le=730, description="Episode duration in days")
    inclusion_criteria: List[str] = Field(..., min_items=1, description="Criteria for episode inclusion")
    exclusion_criteria: List[str] = Field(default_factory=list, description="Criteria for episode exclusion")


# ============================================================================
# COMPONENT 5: POPULATION IDENTIFICATION
# ============================================================================

class CohortCriteria(BaseModel):
    """Cohort identification criteria"""
    diagnosis_codes: List[str] = Field(default_factory=list, description="ICD-10 diagnosis codes")
    procedure_codes: List[str] = Field(default_factory=list, description="CPT/HCPCS procedure codes")
    medication_codes: List[str] = Field(default_factory=list, description="NDC medication codes")
    age_range: Optional[Dict[str, int]] = Field(None, description="Age range (min/max)")
    enrollment_criteria: Optional[str] = Field(None, description="Enrollment requirements")
    minimum_claims: Optional[int] = Field(None, ge=1, description="Minimum claim count")


class StratificationVariable(BaseModel):
    """Variable for cohort stratification"""
    variable_name: str = Field(..., description="Variable name (e.g., age_group)")
    variable_type: Literal["categorical", "numeric", "boolean"] = Field(..., description="Variable type")
    categories: Optional[List[str]] = Field(None, description="Categories for categorical variables")
    calculation_logic: Optional[str] = Field(None, description="Logic for calculating variable")


class PopulationIdentification(BaseModel):
    """Population/cohort identification"""
    cohort_name: str = Field(..., description="Cohort name")
    cohort_description: str = Field(..., min_length=20, description="Cohort description")
    inclusion_criteria: CohortCriteria = Field(..., description="Criteria for cohort inclusion")
    exclusion_criteria: Optional[CohortCriteria] = Field(None, description="Criteria for cohort exclusion")
    stratification_variables: List[StratificationVariable] = Field(default_factory=list, description="Variables for stratification")
    sql_template: str = Field(..., min_length=100, description="SQL template for cohort identification")

    @field_validator('sql_template')
    @classmethod
    def validate_sql_template(cls, v: str) -> str:
        if 'SELECT' not in v.upper():
            raise ValueError("SQL template must contain SELECT statement")
        return v


# ============================================================================
# COMPONENT 6: BASELINE METHODOLOGY
# ============================================================================

class TimePeriod(BaseModel):
    """Time period definition"""
    period_name: str = Field(..., description="Period name (e.g., baseline, intervention)")
    duration_months: int = Field(..., ge=1, le=60, description="Period duration in months")
    offset_months: int = Field(default=0, description="Offset from reference date")


class BaselineMethodology(BaseModel):
    """Baseline calculation methodology"""
    time_periods: List[TimePeriod] = Field(..., min_items=1, description="Time periods (baseline, intervention)")
    trend_analysis_method: Literal["linear", "seasonal", "none"] = Field(default="linear", description="Trend analysis method")
    risk_adjustment_method: Optional[str] = Field(None, description="Risk adjustment methodology")
    normalization_method: Optional[str] = Field(None, description="Data normalization method")
    baseline_calculation_logic: str = Field(..., min_length=50, description="Logic for baseline calculation")

    @model_validator(mode='after')
    def validate_periods(self):
        if len(self.time_periods) < 1:
            raise ValueError("At least one time period required (baseline)")
        return self


# ============================================================================
# COMPONENT 7: CALCULATION COMPONENTS
# ============================================================================

class Variable(BaseModel):
    """Variable definition"""
    variable_name: str = Field(..., description="Variable name")
    variable_type: Literal["input", "intermediate", "output"] = Field(..., description="Variable type")
    data_type: Literal["integer", "float", "boolean", "string"] = Field(..., description="Data type")
    description: str = Field(..., min_length=10, description="Variable description")
    source: Optional[str] = Field(None, description="Data source for variable")
    default_value: Optional[Any] = Field(None, description="Default value if missing")


class Formula(BaseModel):
    """Calculation formula"""
    formula_name: str = Field(..., description="Formula name")
    formula_expression: str = Field(..., description="Mathematical expression")
    variables_used: List[str] = Field(..., min_items=1, description="Variables used in formula")
    output_variable: str = Field(..., description="Output variable name")
    description: str = Field(..., min_length=10, description="Formula description")


class Calculation(BaseModel):
    """Individual calculation step"""
    step_number: int = Field(..., ge=1, description="Calculation step number")
    step_name: str = Field(..., description="Step name")
    formula: Formula = Field(..., description="Formula for this step")
    dependencies: List[int] = Field(default_factory=list, description="Dependent step numbers")


class CalculationComponents(BaseModel):
    """All calculation components"""
    variables: List[Variable] = Field(..., min_items=1, description="All variables")
    formulas: List[Formula] = Field(..., min_items=1, description="All formulas")
    calculations: List[Calculation] = Field(..., min_items=1, description="Calculation steps")

    @model_validator(mode='after')
    def validate_calculations(self):
        # Validate step numbers are sequential
        step_numbers = [c.step_number for c in self.calculations]
        expected = list(range(1, len(self.calculations) + 1))
        if sorted(step_numbers) != expected:
            raise ValueError("Calculation steps must be sequential starting from 1")
        return self


# ============================================================================
# COMPONENT 8: SQL COMPONENTS
# ============================================================================

class SQLQuery(BaseModel):
    """SQL query definition"""
    query_name: str = Field(..., description="Query name")
    query_type: Literal["cohort", "baseline", "intervention", "metric", "validation"] = Field(..., description="Query type")
    sql_template: str = Field(..., min_length=50, description="SQL query template")
    parameters: List[str] = Field(default_factory=list, description="Query parameters")
    output_schema: Dict[str, str] = Field(..., description="Output schema (column: type)")


class SQLComponents(BaseModel):
    """SQL components for data extraction"""
    queries: List[SQLQuery] = Field(..., min_items=1, description="SQL queries")
    common_table_expressions: Optional[List[str]] = Field(None, description="Reusable CTEs")

    @field_validator('queries')
    @classmethod
    def validate_queries(cls, v: List[SQLQuery]) -> List[SQLQuery]:
        if not v or len(v) == 0:
            raise ValueError("At least one SQL query required")
        return v


# ============================================================================
# COMPONENT 9: OUTPUT METRICS
# ============================================================================

class Metric(BaseModel):
    """Individual output metric"""
    metric_name: str = Field(..., description="Metric name")
    metric_type: MetricType = Field(..., description="Metric type")
    calculation_method: str = Field(..., min_length=20, description="How metric is calculated")
    unit_of_measure: str = Field(..., description="Unit (e.g., $, %, days)")
    display_format: str = Field(default="{:,.2f}", description="Display format string")
    benchmark_value: Optional[float] = Field(None, description="Industry benchmark")


class OutputMetrics(BaseModel):
    """All output metrics"""
    primary_metrics: List[Metric] = Field(..., min_items=1, description="Primary ROI metrics")
    secondary_metrics: List[Metric] = Field(default_factory=list, description="Secondary/supporting metrics")

    @field_validator('primary_metrics')
    @classmethod
    def validate_primary_metrics(cls, v: List[Metric]) -> List[Metric]:
        if not v or len(v) == 0:
            raise ValueError("At least one primary metric required")
        return v


# ============================================================================
# COMPONENT 10: ASSUMPTIONS
# ============================================================================

class Assumption(BaseModel):
    """Individual assumption"""
    assumption_id: str = Field(..., description="Unique assumption ID")
    category: Literal["clinical", "financial", "operational", "behavioral"] = Field(..., description="Assumption category")
    description: str = Field(..., min_length=20, description="Assumption description")
    value: Any = Field(..., description="Assumption value")
    confidence_level: Literal["high", "medium", "low"] = Field(..., description="Confidence level")
    source: Optional[str] = Field(None, description="Source of assumption")
    sensitivity_impact: Literal["high", "medium", "low"] = Field(..., description="Impact on results if changed")


class Assumptions(BaseModel):
    """All model assumptions"""
    assumptions: List[Assumption] = Field(..., min_items=1, description="List of assumptions")

    @field_validator('assumptions')
    @classmethod
    def validate_assumptions(cls, v: List[Assumption]) -> List[Assumption]:
        if not v or len(v) == 0:
            raise ValueError("At least one assumption required")
        # Check for unique IDs
        ids = [a.assumption_id for a in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Assumption IDs must be unique")
        return v


# ============================================================================
# COMPONENT 11: VALIDATION RULES
# ============================================================================

class ValidationRule(BaseModel):
    """Data validation rule"""
    rule_id: str = Field(..., description="Unique rule ID")
    rule_type: Literal["data_quality", "business_logic", "threshold", "consistency"] = Field(..., description="Rule type")
    description: str = Field(..., min_length=20, description="Rule description")
    validation_logic: str = Field(..., description="Validation logic expression")
    error_message: str = Field(..., description="Error message if validation fails")
    severity: Literal["critical", "warning", "info"] = Field(default="warning", description="Severity level")


class ValidationRules(BaseModel):
    """All validation rules"""
    rules: List[ValidationRule] = Field(..., min_items=1, description="Validation rules")

    @field_validator('rules')
    @classmethod
    def validate_rules(cls, v: List[ValidationRule]) -> List[ValidationRule]:
        if not v or len(v) == 0:
            raise ValueError("At least one validation rule required")
        # Check for unique IDs
        ids = [r.rule_id for r in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Validation rule IDs must be unique")
        return v


# ============================================================================
# COMPONENT 12: CONFIDENCE FACTORS
# ============================================================================

class ConfidenceFactor(BaseModel):
    """Factor affecting confidence in results"""
    factor_name: str = Field(..., description="Factor name")
    impact_on_confidence: Literal["increases", "decreases", "neutral"] = Field(..., description="Impact direction")
    magnitude: Literal["high", "medium", "low"] = Field(..., description="Impact magnitude")
    description: str = Field(..., min_length=20, description="Factor description")
    mitigation_strategy: Optional[str] = Field(None, description="How to mitigate negative impact")


class ConfidenceFactors(BaseModel):
    """Factors affecting model confidence"""
    overall_confidence: Literal["high", "medium", "low"] = Field(..., description="Overall model confidence")
    confidence_factors: List[ConfidenceFactor] = Field(..., min_items=1, description="Individual confidence factors")

    @field_validator('confidence_factors')
    @classmethod
    def validate_factors(cls, v: List[ConfidenceFactor]) -> List[ConfidenceFactor]:
        if not v or len(v) == 0:
            raise ValueError("At least one confidence factor required")
        return v


# ============================================================================
# COMPONENT 13: CONFIGURABLE PARAMETERS
# ============================================================================

class Parameter(BaseModel):
    """Configurable parameter"""
    parameter_name: str = Field(..., description="Parameter name")
    parameter_type: ParameterType = Field(..., description="Parameter type")
    default_value: Any = Field(..., description="Default value")
    min_value: Optional[float] = Field(None, description="Minimum allowed value")
    max_value: Optional[float] = Field(None, description="Maximum allowed value")
    description: str = Field(..., min_length=10, description="Parameter description")
    user_configurable: bool = Field(default=True, description="Can user change this?")


class ConfigurableParameters(BaseModel):
    """All configurable parameters"""
    time_parameters: List[Parameter] = Field(default_factory=list, description="Time-related parameters")
    rate_parameters: List[Parameter] = Field(default_factory=list, description="Rate parameters")
    cost_parameters: List[Parameter] = Field(default_factory=list, description="Cost parameters")
    threshold_parameters: List[Parameter] = Field(default_factory=list, description="Threshold parameters")

    @model_validator(mode='after')
    def validate_parameters(self):
        all_params = (
            self.time_parameters +
            self.rate_parameters +
            self.cost_parameters +
            self.threshold_parameters
        )
        if len(all_params) == 0:
            raise ValueError("At least one configurable parameter required")
        return self


# ============================================================================
# COMPONENT 14: DASHBOARD TEMPLATES
# ============================================================================

class DashboardWidget(BaseModel):
    """Dashboard widget specification"""
    widget_id: str = Field(..., description="Unique widget ID")
    widget_type: Literal["metric", "chart", "table", "text"] = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    data_source: str = Field(..., description="Data source (metric name or query)")
    visualization_config: Dict[str, Any] = Field(default_factory=dict, description="Visualization configuration")


class DashboardTemplate(BaseModel):
    """Dashboard template"""
    template_id: str = Field(..., description="Unique template ID")
    template_name: str = Field(..., description="Template name")
    target_audience: Literal["executive", "clinical", "operational", "financial"] = Field(..., description="Target audience")
    widgets: List[DashboardWidget] = Field(..., min_items=1, description="Dashboard widgets")
    layout_config: Optional[Dict[str, Any]] = Field(None, description="Layout configuration")


class DashboardTemplates(BaseModel):
    """Dashboard templates"""
    templates: List[DashboardTemplate] = Field(..., min_items=1, description="Dashboard templates")

    @field_validator('templates')
    @classmethod
    def validate_templates(cls, v: List[DashboardTemplate]) -> List[DashboardTemplate]:
        if not v or len(v) == 0:
            raise ValueError("At least one dashboard template required")
        # Check for unique IDs
        ids = [t.template_id for t in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Dashboard template IDs must be unique")
        return v


# ============================================================================
# COMPONENT 15: ROOT MODEL - ROI MODEL JSON
# ============================================================================

class ROIModelJSON(BaseModel):
    """
    Complete ROI Model JSON structure

    This is the root model containing all 15 components required for
    a complete ROI model definition and execution.
    """
    # Required components
    model_metadata: ROIModelMetadata = Field(..., description="Model metadata")
    executive_summary: ExecutiveSummary = Field(..., description="Executive summary")
    data_requirements: DataRequirements = Field(..., description="Data requirements")
    population_identification: PopulationIdentification = Field(..., description="Population/cohort identification")
    baseline_methodology: BaselineMethodology = Field(..., description="Baseline methodology")
    calculation_components: CalculationComponents = Field(..., description="Calculation components")
    sql_components: SQLComponents = Field(..., description="SQL components")
    output_metrics: OutputMetrics = Field(..., description="Output metrics")
    assumptions: Assumptions = Field(..., description="Model assumptions")
    validation_rules: ValidationRules = Field(..., description="Validation rules")
    confidence_factors: ConfidenceFactors = Field(..., description="Confidence factors")
    configurable_parameters: ConfigurableParameters = Field(..., description="Configurable parameters")
    dashboard_templates: DashboardTemplates = Field(..., description="Dashboard templates")

    # Optional components
    episode_definition: Optional[EpisodeDefinition] = Field(None, description="Episode definition (for episode-based models)")

    # Additional metadata
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    generation_source: Literal["agent", "manual", "imported"] = Field(default="agent", description="How model was generated")

    @model_validator(mode='after')
    def validate_roi_model(self):
        """Cross-component validation"""
        # Validate episode definition required for episode-based models
        if self.model_metadata.model_type_code == ModelTypeCode.B7:
            if not self.episode_definition:
                raise ValueError("Episode definition required for B7 (Episode Optimization) models")

        return self


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_roi_model(roi_model: ROIModelJSON) -> Dict[str, Any]:
    """
    Comprehensive validation of ROI Model JSON

    Performs 4-layer validation:
    1. Pydantic validation (automatic)
    2. Business rule validation
    3. Cross-component consistency checks
    4. Completeness checks

    Args:
        roi_model: ROIModelJSON instance to validate

    Returns:
        Dict with validation results:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str],
            "info": Dict[str, Any]
        }
    """
    errors = []
    warnings = []
    info = {}

    # Business rule validations
    try:
        # Check 1: Verify all calculation variables are defined
        defined_variables = {v.variable_name for v in roi_model.calculation_components.variables}
        used_variables = set()
        for formula in roi_model.calculation_components.formulas:
            used_variables.update(formula.variables_used)

        undefined_vars = used_variables - defined_variables
        if undefined_vars:
            errors.append(f"Undefined variables used in formulas: {undefined_vars}")

        # Check 2: Verify output metrics reference valid calculations
        output_vars = {f.output_variable for f in roi_model.calculation_components.formulas}
        for metric in roi_model.output_metrics.primary_metrics:
            # This is a simplified check - real validation would parse calculation_method
            pass

        # Check 3: Verify SQL queries have valid parameters
        for query in roi_model.sql_components.queries:
            if query.parameters:
                # Check parameters are mentioned in SQL template
                for param in query.parameters:
                    if f":{param}" not in query.sql_template and f"{{{param}}}" not in query.sql_template:
                        warnings.append(f"Parameter '{param}' not found in query '{query.query_name}' template")

        # Check 4: Verify dashboard widgets reference valid data sources
        all_metrics = [m.metric_name for m in roi_model.output_metrics.primary_metrics]
        all_metrics.extend([m.metric_name for m in roi_model.output_metrics.secondary_metrics])
        all_queries = [q.query_name for q in roi_model.sql_components.queries]

        for template in roi_model.dashboard_templates.templates:
            for widget in template.widgets:
                if widget.data_source not in all_metrics and widget.data_source not in all_queries:
                    warnings.append(f"Widget '{widget.widget_id}' references unknown data source '{widget.data_source}'")

        # Check 5: Validate minimum component counts
        if len(roi_model.calculation_components.calculations) < 3:
            warnings.append("Model has fewer than 3 calculation steps - may be incomplete")

        if len(roi_model.output_metrics.primary_metrics) < 3:
            warnings.append("Model has fewer than 3 primary metrics - consider adding more")

        # Collect info
        info['model_type'] = roi_model.model_metadata.model_type_code.value
        info['client_name'] = roi_model.model_metadata.client_name
        info['total_variables'] = len(roi_model.calculation_components.variables)
        info['total_calculations'] = len(roi_model.calculation_components.calculations)
        info['total_metrics'] = len(roi_model.output_metrics.primary_metrics) + len(roi_model.output_metrics.secondary_metrics)
        info['total_assumptions'] = len(roi_model.assumptions.assumptions)
        info['total_sql_queries'] = len(roi_model.sql_components.queries)
        info['total_dashboard_templates'] = len(roi_model.dashboard_templates.templates)
        info['overall_confidence'] = roi_model.confidence_factors.overall_confidence

    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": info
    }


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON from agent response (handles markdown code blocks)

    Args:
        response_text: Raw response text from agent

    Returns:
        Extracted JSON string
    """
    import re

    # Try to extract from markdown code block
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # Try to find JSON object directly
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        return json_match.group(0)

    # Return as-is if no extraction patterns match
    return response_text


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example minimal ROI model for testing
    example_model = {
        "model_metadata": {
            "model_type_code": "B1",
            "model_type_name": "Unit Price Optimization",
            "client_name": "Test Client",
            "version": "1.0.0",
            "status": "draft"
        },
        "executive_summary": {
            "problem_statement": "High costs for MSK procedures compared to market rates",
            "solution_approach": "Identify high-cost procedures and negotiate better rates",
            "expected_impact": "15-20% reduction in MSK procedure costs",
            "key_assumptions": ["Market rates available", "Volume commitments feasible"],
            "target_population_size": 5000,
            "estimated_annual_savings": 1500000.0
        },
        "data_requirements": {
            "data_sources": [
                {
                    "source_name": "medical_claims",
                    "source_type": "claims",
                    "required_fields": ["member_id", "service_date", "procedure_code", "paid_amount"],
                    "date_range_required": True,
                    "join_keys": ["member_id"]
                }
            ],
            "minimum_lookback_months": 12,
            "data_quality_requirements": ["Complete member enrollment", "Valid procedure codes"]
        },
        "population_identification": {
            "cohort_name": "MSK High-Cost Population",
            "cohort_description": "Members with high-cost MSK procedures",
            "inclusion_criteria": {
                "diagnosis_codes": ["M79.1", "M79.2"],
                "procedure_codes": ["29881", "29882"],
                "minimum_claims": 2
            },
            "sql_template": "SELECT member_id FROM medical_claims WHERE diagnosis_code IN (:diagnosis_codes)"
        },
        "baseline_methodology": {
            "time_periods": [
                {"period_name": "baseline", "duration_months": 12, "offset_months": 0}
            ],
            "trend_analysis_method": "linear",
            "baseline_calculation_logic": "Calculate average cost per procedure in baseline period"
        },
        "calculation_components": {
            "variables": [
                {
                    "variable_name": "baseline_cost",
                    "variable_type": "input",
                    "data_type": "float",
                    "description": "Average baseline cost per procedure",
                    "source": "medical_claims"
                }
            ],
            "formulas": [
                {
                    "formula_name": "savings_calculation",
                    "formula_expression": "(baseline_cost - target_cost) * volume",
                    "variables_used": ["baseline_cost", "target_cost", "volume"],
                    "output_variable": "total_savings",
                    "description": "Calculate total savings"
                }
            ],
            "calculations": [
                {
                    "step_number": 1,
                    "step_name": "Calculate savings",
                    "formula": {
                        "formula_name": "savings_calculation",
                        "formula_expression": "(baseline_cost - target_cost) * volume",
                        "variables_used": ["baseline_cost", "target_cost", "volume"],
                        "output_variable": "total_savings",
                        "description": "Calculate total savings"
                    },
                    "dependencies": []
                }
            ]
        },
        "sql_components": {
            "queries": [
                {
                    "query_name": "baseline_costs",
                    "query_type": "baseline",
                    "sql_template": "SELECT AVG(paid_amount) FROM medical_claims WHERE service_date BETWEEN :start_date AND :end_date",
                    "parameters": ["start_date", "end_date"],
                    "output_schema": {"avg_cost": "float"}
                }
            ]
        },
        "output_metrics": {
            "primary_metrics": [
                {
                    "metric_name": "total_savings",
                    "metric_type": "financial",
                    "calculation_method": "Sum of all procedure savings",
                    "unit_of_measure": "$",
                    "display_format": "${:,.2f}"
                }
            ]
        },
        "assumptions": {
            "assumptions": [
                {
                    "assumption_id": "A1",
                    "category": "financial",
                    "description": "Market rates are 20% below current rates",
                    "value": 0.20,
                    "confidence_level": "medium",
                    "sensitivity_impact": "high"
                }
            ]
        },
        "validation_rules": {
            "rules": [
                {
                    "rule_id": "V1",
                    "rule_type": "data_quality",
                    "description": "All costs must be positive",
                    "validation_logic": "paid_amount > 0",
                    "error_message": "Negative cost detected",
                    "severity": "critical"
                }
            ]
        },
        "confidence_factors": {
            "overall_confidence": "medium",
            "confidence_factors": [
                {
                    "factor_name": "Data completeness",
                    "impact_on_confidence": "increases",
                    "magnitude": "high",
                    "description": "Complete 24-month claims history available"
                }
            ]
        },
        "configurable_parameters": {
            "time_parameters": [
                {
                    "parameter_name": "baseline_months",
                    "parameter_type": "time",
                    "default_value": 12,
                    "min_value": 6,
                    "max_value": 24,
                    "description": "Baseline period duration",
                    "user_configurable": True
                }
            ]
        },
        "dashboard_templates": {
            "templates": [
                {
                    "template_id": "T1",
                    "template_name": "Executive Summary",
                    "target_audience": "executive",
                    "widgets": [
                        {
                            "widget_id": "W1",
                            "widget_type": "metric",
                            "title": "Total Savings",
                            "data_source": "total_savings",
                            "visualization_config": {}
                        }
                    ]
                }
            ]
        }
    }

    try:
        model = ROIModelJSON(**example_model)
        validation = validate_roi_model(model)
        print(f"Validation result: {validation}")
    except Exception as e:
        print(f"Validation failed: {e}")

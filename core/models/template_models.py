"""Pydantic models for Dashboard Template Generation.

These models match the frontend TypeScript types exactly from:
src/types/dashboardTemplateTypes.ts
"""

from typing import List, Optional, Literal, Any, Dict, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class WidgetPosition(BaseModel):
    """Widget position in 12-column grid."""
    row: int = Field(..., ge=1, description="Grid row (1-indexed)")
    col: int = Field(..., ge=1, description="Grid column (1-indexed)")
    rowSpan: int = Field(..., ge=1, description="Height in grid units")
    colSpan: int = Field(..., ge=1, le=12, description="Width in grid units (max 12)")


# =============================================================================
# Data Requirements Models (NEW)
# =============================================================================

class FilterDefinition(BaseModel):
    """SQL filter/WHERE clause definition."""
    field: str = Field(..., description="Column or field name")
    operator: Literal['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'in', 'between', 'like'] = Field(
        ..., description="Comparison operator"
    )
    value: Union[str, int, float, List[Union[str, int, float]]] = Field(
        ..., description="Filter value(s)"
    )


class TimeRange(BaseModel):
    """Time range specification for time-series queries."""
    type: Literal['relative', 'absolute'] = Field(..., description="Time range type")
    value: str = Field(..., description="Time range value (e.g., 'last_12_months', '2024-01-01')")


class MetricDefinition(BaseModel):
    """Definition of a metric to be calculated."""
    name: str = Field(..., description="Metric name for referencing in results")
    metric_ref: Optional[str] = Field(
        None, description="Reference to metrics_library (e.g., 'member_count')"
    )
    expression: Optional[str] = Field(
        None, description="Custom SQL expression (e.g., 'AVG(baseline_hba1c - current_hba1c)')"
    )
    data_type: Literal['count', 'currency', 'percentage', 'number'] = Field(
        ..., description="Type of data this metric produces"
    )
    format: str = Field(..., description="Number format pattern (e.g., '0,0', '$0.0a', '0.0%')")


class DataRequirements(BaseModel):
    """Data requirements specification for a widget."""
    query_type: Literal['aggregate', 'time-series', 'distribution', 'comparison'] = Field(
        ..., description="Type of query to execute"
    )
    metrics: List[MetricDefinition] = Field(
        default_factory=list, description="Metrics to calculate"
    )
    dimensions: Optional[List[str]] = Field(
        None, description="Dimensions for GROUP BY (e.g., ['month', 'category'])"
    )
    filters: Optional[List[FilterDefinition]] = Field(
        None, description="Filters for WHERE clause"
    )
    time_range: Optional[TimeRange] = Field(
        None, description="Time range for time-series queries"
    )


class DashboardWidget(BaseModel):
    """Single widget configuration."""
    id: str = Field(..., description="Unique widget identifier")
    type: Literal[
        # KPI & Metrics
        'kpi-card', 'kpi-grid', 'metric-comparison', 'scorecard',
        # Line Charts
        'line-chart', 'multi-line-chart', 'area-chart', 'stacked-area-chart',
        # Bar Charts
        'bar-chart', 'horizontal-bar-chart', 'stacked-bar-chart', 'grouped-bar-chart',
        # Pie & Donut
        'pie-chart', 'donut-chart',
        # Specialized
        'waterfall-chart', 'scatter-plot', 'bubble-chart', 'radar-chart', 'polar-area-chart',
        # Custom
        'progress-bar', 'gauge-chart', 'timeline-chart', 'quality-progression',
        'ranked-list', 'data-table', 'heatmap', 'trend-sparkline',
        # Advanced (ApexCharts-focused)
        'treemap', 'funnel-chart', 'candlestick-chart', 'box-plot',
        'radial-bar-chart', 'range-bar-chart', 'slope-chart',
        # Composite
        'roi-summary', 'clinical-metrics', 'cost-breakdown'
    ] = Field(..., description="Widget type")
    title: str = Field(..., min_length=5, max_length=100, description="Widget display title")
    description: Optional[str] = Field(
        None, description="Widget description explaining what it shows"
    )
    position: WidgetPosition

    # NEW: Data requirements and analytics question
    data_requirements: Optional[DataRequirements] = Field(
        None, description="Data requirements specification (metrics, filters, etc.)"
    )
    analytics_question: Optional[str] = Field(
        None, description="Business question this widget answers (e.g., 'How many members are enrolled?')"
    )

    # Data populated at runtime
    data: Dict[str, Any] = Field(default_factory=dict, description="Populated by Analytics Team later")

    # Visualization config
    chartType: Optional[Literal['line', 'bar', 'pie', 'waterfall', 'area', 'donut']] = Field(
        None, description="Chart type (only if type='chart')"
    )
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Widget-specific config")


class VisualStyle(BaseModel):
    """Visual styling for template."""
    primaryColor: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Primary color (hex)")
    accentColor: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Accent color (hex)")
    secondaryColor: str = Field(
        default="#64748b", pattern=r'^#[0-9A-Fa-f]{6}$', description="Secondary color (hex)"
    )
    backgroundColor: str = Field(
        default="#ffffff", pattern=r'^#[0-9A-Fa-f]{6}$', description="Background color (hex)"
    )
    textColor: str = Field(
        default="#1e293b", pattern=r'^#[0-9A-Fa-f]{6}$', description="Text color (hex)"
    )
    fontFamily: str = Field(
        default="Inter, system-ui, sans-serif", description="Font family"
    )
    layout: Literal['dense', 'balanced', 'spacious'] = Field(..., description="Layout density")


class DashboardTemplate(BaseModel):
    """Complete dashboard template definition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique template ID")
    name: str = Field(..., min_length=5, max_length=100, description="Template display name")
    description: str = Field(..., min_length=20, max_length=500, description="Template purpose and focus")
    category: Literal[
        'roi-focused',
        'clinical-outcomes',
        'operational-efficiency',
        'competitive-positioning',
        'comprehensive'
    ] = Field(..., description="Template category")
    targetAudience: str = Field(..., description="Target audience (Health Plan, Broker, PBM, TPA, Medical Management)")
    keyFeatures: List[str] = Field(..., min_items=3, max_items=5, description="3-5 key features")
    widgets: List[DashboardWidget] = Field(..., min_items=6, max_items=12, description="6-12 widgets per template")
    visualStyle: VisualStyle
    recommendedUseCase: Optional[str] = Field(None, description="When and how to use this template")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Diabetes ROI Executive Dashboard",
                "description": "C-suite focused financial impact dashboard showing 24-month ROI and savings",
                "category": "roi-focused",
                "targetAudience": "Health Plan",
                "keyFeatures": [
                    "24-month ROI with trend analysis",
                    "Cost savings waterfall by category",
                    "Payback period visualization"
                ],
                "widgets": [
                    {
                        "id": "w_roi_24mo",
                        "type": "kpi-card",
                        "title": "24-Month ROI",
                        "position": {"row": 1, "col": 1, "rowSpan": 2, "colSpan": 3},
                        "data": {},
                        "config": {"format": "percentage", "trend": True}
                    }
                ],
                "visualStyle": {
                    "primaryColor": "#2563eb",
                    "accentColor": "#10b981",
                    "layout": "balanced"
                },
                "recommendedUseCase": "Executive presentations to C-suite"
            }
        }


class SingleTemplateResult(BaseModel):
    """Result from generating a single template."""
    template: DashboardTemplate
    reasoning: Optional[str] = Field(None, description="Brief explanation of template design choices")

    class Config:
        json_schema_extra = {
            "example": {
                "template": {
                    "id": "uuid1",
                    "name": "Diabetes ROI Executive Dashboard",
                    "description": "C-suite focused financial impact dashboard showing 24-month ROI",
                    "category": "roi-focused",
                    "targetAudience": "Health Plan",
                    "keyFeatures": ["24-month ROI", "Savings waterfall", "Payback period"],
                    "widgets": [],
                    "visualStyle": {
                        "primaryColor": "#2563eb",
                        "accentColor": "#10b981",
                        "layout": "balanced"
                    }
                },
                "reasoning": "Designed for C-suite executives who need quick ROI visibility"
            }
        }


class TemplateGenerationMetadata(BaseModel):
    """Metadata about template generation process."""
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    industry: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_templates: int = 0
    validation_passed: bool = False
    generation_time_seconds: Optional[float] = None


class TemplateGenerationResult(BaseModel):
    """Complete result from template generation agent."""
    templates: List[DashboardTemplate] = Field(..., min_items=5, max_items=10, description="5-10 generated templates")
    metadata: TemplateGenerationMetadata
    unmapped_categories: List[str] = Field(default_factory=list, description="Categories not covered")
    unmapped_audiences: List[str] = Field(default_factory=list, description="Audiences not covered")

    class Config:
        json_schema_extra = {
            "example": {
                "templates": [
                    {
                        "id": "uuid1",
                        "name": "Diabetes ROI Executive Dashboard",
                        "description": "C-suite focused financial impact dashboard",
                        "category": "roi-focused",
                        "targetAudience": "Health Plan",
                        "keyFeatures": ["24-month ROI", "Savings waterfall", "Payback period"],
                        "widgets": [],
                        "visualStyle": {
                            "primaryColor": "#2563eb",
                            "accentColor": "#10b981",
                            "layout": "balanced"
                        }
                    }
                ],
                "metadata": {
                    "client_id": "client-uuid-123",
                    "client_name": "Livongo Health",
                    "industry": "Diabetes Management",
                    "generated_at": "2025-01-15T12:00:00Z",
                    "total_templates": 7,
                    "validation_passed": True,
                    "generation_time_seconds": 45.2
                },
                "unmapped_categories": [],
                "unmapped_audiences": []
            }
        }


# Validation helper functions

def validate_data_requirements(templates: List[DashboardTemplate]) -> List[str]:
    """
    Validate that widgets have proper data_requirements.

    Returns list of validation errors.
    """
    errors = []

    for template in templates:
        for widget in template.widgets:
            widget_id = widget.id

            # Check if data_requirements exists
            if not widget.data_requirements:
                errors.append(f"Widget '{widget_id}' in template '{template.name}' missing data_requirements")
                continue

            # Check if metrics list is not empty
            if not widget.data_requirements.metrics or len(widget.data_requirements.metrics) == 0:
                errors.append(f"Widget '{widget_id}' in template '{template.name}' has empty metrics list")

            # Validate each metric has either metric_ref or expression
            for i, metric in enumerate(widget.data_requirements.metrics):
                if not metric.metric_ref and not metric.expression:
                    errors.append(
                        f"Widget '{widget_id}' metric #{i} in template '{template.name}' "
                        f"must have either 'metric_ref' or 'expression'"
                    )

    return errors


def validate_analytics_questions(templates: List[DashboardTemplate]) -> List[str]:
    """
    Validate that widgets have meaningful analytics_question.

    Returns list of validation errors.
    """
    errors = []

    for template in templates:
        for widget in template.widgets:
            widget_id = widget.id

            # Check if analytics_question exists and is not empty
            if not widget.analytics_question or widget.analytics_question.strip() == "":
                errors.append(
                    f"Widget '{widget_id}' in template '{template.name}' "
                    f"missing or empty analytics_question"
                )

    return errors


def validate_template_count(templates: List[DashboardTemplate]) -> None:
    """Validate template count is between 5-10."""
    count = len(templates)
    if count < 5 or count > 10:
        raise ValueError(f"Must generate 5-10 templates, got {count}")


def validate_widget_counts(templates: List[DashboardTemplate]) -> None:
    """Validate each template has 6-12 widgets."""
    for template in templates:
        widget_count = len(template.widgets)
        if widget_count < 6 or widget_count > 12:
            raise ValueError(
                f"Template '{template.name}' has {widget_count} widgets, must be 6-12"
            )


def validate_category_coverage(templates: List[DashboardTemplate]) -> List[str]:
    """Validate all categories are represented. Returns list of missing categories."""
    required_categories = {
        'roi-focused',
        'clinical-outcomes',
        'operational-efficiency',
        'competitive-positioning',
        'comprehensive'
    }

    present_categories = {t.category for t in templates}
    missing = list(required_categories - present_categories)
    return missing


def validate_audience_coverage(
    templates: List[DashboardTemplate],
    target_audiences: List[str]
) -> List[str]:
    """Validate all target audiences are covered. Returns list of missing audiences."""
    present_audiences = {t.targetAudience for t in templates}
    missing = [aud for aud in target_audiences if aud not in present_audiences]
    return missing


def validate_grid_positions(template: DashboardTemplate) -> None:
    """Validate widget positions don't overlap and fit in grid."""
    occupied_cells = set()

    for widget in template.widgets:
        pos = widget.position

        # Validate column span doesn't exceed grid
        if pos.col + pos.colSpan > 13:
            raise ValueError(
                f"Widget '{widget.id}' exceeds 12-column grid: "
                f"col {pos.col} + colSpan {pos.colSpan} > 12"
            )

        # Get all cells this widget occupies
        cells = {
            (row, col)
            for row in range(pos.row, pos.row + pos.rowSpan)
            for col in range(pos.col, pos.col + pos.colSpan)
        }

        # Check for overlaps
        overlap = occupied_cells & cells
        if overlap:
            raise ValueError(
                f"Widget '{widget.id}' overlaps with another widget at positions: {overlap}"
            )

        occupied_cells.update(cells)


def validate_widget_config_by_type(templates: List[DashboardTemplate]) -> List[str]:
    """
    Validate widget has required config fields for its type.

    Returns list of validation errors.
    """
    errors = []

    # Define required config fields per widget type
    required_fields = {
        # KPI & Metrics
        'kpi-card': ['icon', 'subtitle'],
        'kpi-grid': ['metrics'],
        'metric-comparison': ['metrics'],
        'scorecard': ['metrics'],

        # Gauge & Progress
        'gauge-chart': ['min_value', 'max_value'],
        'progress-bar': ['target_value'],

        # Tables
        'data-table': ['columns'],

        # Composite widgets
        'roi-summary': [],  # No strict requirements, uses data_points
        'clinical-metrics': ['metrics'],
        'cost-breakdown': [],
    }

    # Define recommended (not required) fields
    recommended_fields = {
        'line-chart': ['x_axis', 'y_axis'],
        'bar-chart': ['x_axis', 'y_axis'],
        'pie-chart': ['show_labels'],
        'donut-chart': ['show_labels', 'inner_radius'],
        'radar-chart': ['show_markers'],
        'heatmap': ['show_values'],
        'funnel-chart': [],
        'timeline-chart': ['show_breakeven_line'],
        'waterfall-chart': ['show_breakeven_line'],
    }

    for template in templates:
        for widget in template.widgets:
            widget_type = widget.type
            config = widget.config or {}

            # Check required fields
            if widget_type in required_fields:
                for field in required_fields[widget_type]:
                    if field not in config or config[field] is None:
                        errors.append(
                            f"Widget '{widget.id}' ({widget_type}) in template '{template.name}' "
                            f"missing required config field: '{field}'"
                        )

            # Check for deprecated usage patterns
            if widget_type == 'kpi-card' and config.get('format'):
                valid_formats = ['currency', 'percentage', 'number']
                if config['format'] not in valid_formats:
                    errors.append(
                        f"Widget '{widget.id}' ({widget_type}) has invalid format: '{config['format']}'. "
                        f"Must be one of: {', '.join(valid_formats)}"
                    )

            # Validate gauge thresholds structure
            if widget_type == 'gauge-chart' and 'thresholds' in config:
                thresholds = config['thresholds']
                if not isinstance(thresholds, list) or len(thresholds) < 2:
                    errors.append(
                        f"Widget '{widget.id}' ({widget_type}) thresholds must be a list with at least 2 entries"
                    )
                else:
                    for i, threshold in enumerate(thresholds):
                        if not isinstance(threshold, dict) or 'value' not in threshold or 'color' not in threshold:
                            errors.append(
                                f"Widget '{widget.id}' ({widget_type}) threshold #{i} must have 'value' and 'color'"
                            )

            # Validate table columns structure
            if widget_type == 'data-table' and 'columns' in config:
                columns = config['columns']
                if not isinstance(columns, list) or len(columns) == 0:
                    errors.append(
                        f"Widget '{widget.id}' ({widget_type}) columns must be a non-empty list"
                    )

            # Validate metric arrays for comparison widgets
            if widget_type in ['metric-comparison', 'scorecard', 'kpi-grid'] and 'metrics' in config:
                metrics = config['metrics']
                if not isinstance(metrics, list) or len(metrics) < 2:
                    errors.append(
                        f"Widget '{widget.id}' ({widget_type}) requires at least 2 metrics"
                    )

    return errors


def validate_widget_size_requirements(templates: List[DashboardTemplate]) -> List[str]:
    """
    Validate widget meets minimum size requirements.

    Returns list of validation errors.
    """
    errors = []

    # Define minimum size requirements (rowSpan, colSpan)
    min_sizes = {
        # KPI widgets can be compact
        'kpi-card': (2, 2),
        'kpi-grid': (2, 6),

        # Charts need more space
        'line-chart': (3, 4),
        'multi-line-chart': (3, 4),
        'area-chart': (3, 4),
        'stacked-area-chart': (3, 4),
        'bar-chart': (3, 3),
        'horizontal-bar-chart': (3, 4),
        'stacked-bar-chart': (3, 4),
        'grouped-bar-chart': (3, 4),
        'pie-chart': (3, 3),
        'donut-chart': (3, 3),
        'gauge-chart': (2, 3),
        'radar-chart': (3, 3),
        'waterfall-chart': (3, 4),
        'scatter-plot': (3, 4),
        'bubble-chart': (3, 4),
        'heatmap': (4, 4),
        'treemap': (3, 4),
        'funnel-chart': (3, 3),

        # Tables need horizontal space
        'data-table': (3, 6),

        # Custom widgets
        'progress-bar': (1, 3),
        'timeline-chart': (3, 6),
        'quality-progression': (3, 4),
        'ranked-list': (3, 3),
        'trend-sparkline': (1, 2),

        # Composite widgets need more space
        'roi-summary': (3, 4),
        'clinical-metrics': (4, 6),
        'cost-breakdown': (3, 6),
        'metric-comparison': (3, 4),
        'scorecard': (3, 4),
    }

    for template in templates:
        for widget in template.widgets:
            widget_type = widget.type
            pos = widget.position

            if widget_type in min_sizes:
                min_rows, min_cols = min_sizes[widget_type]
                if pos.rowSpan < min_rows or pos.colSpan < min_cols:
                    errors.append(
                        f"Widget '{widget.id}' ({widget_type}) in template '{template.name}' is too small: "
                        f"{pos.rowSpan}x{pos.colSpan} (rows x cols). Minimum size: {min_rows}x{min_cols}"
                    )

    return errors


def validate_query_type_compatibility(templates: List[DashboardTemplate]) -> List[str]:
    """
    Validate data requirements query type matches widget type.

    Returns list of validation errors.
    """
    errors = []

    # Define compatible query types per widget type
    compatibility = {
        # Aggregate queries - single values
        'kpi-card': ['aggregate'],
        'kpi-grid': ['aggregate'],
        'gauge-chart': ['aggregate'],
        'progress-bar': ['aggregate'],

        # Time-series queries - temporal data
        'line-chart': ['time-series', 'aggregate'],
        'multi-line-chart': ['time-series'],
        'area-chart': ['time-series', 'aggregate'],
        'stacked-area-chart': ['time-series'],
        'timeline-chart': ['time-series'],
        'trend-sparkline': ['time-series'],

        # Distribution queries - categorical data
        'bar-chart': ['distribution', 'aggregate', 'comparison'],
        'horizontal-bar-chart': ['distribution', 'aggregate', 'comparison'],
        'grouped-bar-chart': ['distribution', 'comparison'],
        'stacked-bar-chart': ['distribution', 'comparison'],
        'pie-chart': ['distribution'],
        'donut-chart': ['distribution'],
        'treemap': ['distribution'],
        'funnel-chart': ['distribution'],
        'waterfall-chart': ['distribution', 'comparison'],

        # Comparison queries
        'metric-comparison': ['comparison', 'aggregate'],
        'scorecard': ['comparison', 'aggregate'],

        # Multi-dimensional
        'radar-chart': ['comparison', 'aggregate'],
        'scatter-plot': ['distribution', 'comparison'],
        'bubble-chart': ['distribution', 'comparison'],
        'heatmap': ['distribution', 'time-series'],

        # Ranking queries
        'ranked-list': ['distribution', 'aggregate'],

        # Tables - flexible
        'data-table': ['aggregate', 'time-series', 'distribution', 'comparison'],

        # Composite widgets
        'roi-summary': ['aggregate'],
        'clinical-metrics': ['comparison', 'aggregate'],
        'cost-breakdown': ['distribution'],
        'quality-progression': ['time-series', 'comparison'],
    }

    for template in templates:
        for widget in template.widgets:
            if not widget.data_requirements:
                continue

            widget_type = widget.type
            query_type = widget.data_requirements.query_type

            if widget_type in compatibility:
                if query_type not in compatibility[widget_type]:
                    errors.append(
                        f"Widget '{widget.id}' ({widget_type}) in template '{template.name}' "
                        f"incompatible with query type '{query_type}'. "
                        f"Compatible types: {', '.join(compatibility[widget_type])}"
                    )

    return errors


def validate_all(
    result: TemplateGenerationResult,
    target_audiences: List[str]
) -> Dict[str, Any]:
    """Run all validation checks. Returns validation report."""
    errors = []
    warnings = []

    try:
        # Validate template count
        validate_template_count(result.templates)
    except ValueError as e:
        errors.append(str(e))

    try:
        # Validate widget counts
        validate_widget_counts(result.templates)
    except ValueError as e:
        errors.append(str(e))

    # NEW: Validate data_requirements
    data_req_errors = validate_data_requirements(result.templates)
    if data_req_errors:
        errors.extend(data_req_errors)

    # NEW: Validate analytics_questions
    analytics_errors = validate_analytics_questions(result.templates)
    if analytics_errors:
        errors.extend(analytics_errors)

    # Validate widget configurations by type
    config_errors = validate_widget_config_by_type(result.templates)
    if config_errors:
        errors.extend(config_errors)

    # Validate widget size requirements
    size_errors = validate_widget_size_requirements(result.templates)
    if size_errors:
        errors.extend(size_errors)

    # Validate query type compatibility
    query_errors = validate_query_type_compatibility(result.templates)
    if query_errors:
        errors.extend(query_errors)

    # Check category coverage
    missing_categories = validate_category_coverage(result.templates)
    if missing_categories:
        warnings.append(f"Missing categories: {', '.join(missing_categories)}")

    # Check audience coverage
    missing_audiences = validate_audience_coverage(result.templates, target_audiences)
    if missing_audiences:
        warnings.append(f"Missing audiences: {', '.join(missing_audiences)}")

    # Validate grid positions for each template
    for template in result.templates:
        try:
            validate_grid_positions(template)
        except ValueError as e:
            errors.append(f"Template '{template.name}': {str(e)}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

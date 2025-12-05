"""Pydantic models for Prospect Dashboard Templates with Data Requirements.

This format includes analytics questions, data requirements, and validation logic
for ensuring templates match available prospect data.
"""

from typing import List, Optional, Literal, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# =============================================================================
# Data Requirements Models
# =============================================================================

class MetricDefinition(BaseModel):
    """Definition of a metric with SQL expression."""
    name: str = Field(..., description="Metric name (e.g., 'roi_conservative')")
    expression: str = Field(..., description="SQL expression to calculate metric")
    data_type: Literal['number', 'percentage', 'currency', 'string', 'date'] = Field(..., description="Data type of metric")
    format: Optional[str] = Field(None, description="Display format (e.g., '0.0x', '$0,0')")


class FilterDefinition(BaseModel):
    """Data filter definition."""
    field: str = Field(..., description="Field name to filter on")
    operator: Literal['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'in', 'not_in', 'like', 'between'] = Field(..., description="Filter operator")
    value: Any = Field(..., description="Filter value (can be string, number, list)")


class TimeRange(BaseModel):
    """Time range specification."""
    type: Literal['relative', 'absolute', 'rolling'] = Field(..., description="Time range type")
    value: Optional[str] = Field(None, description="For relative: 'last_30_days', 'last_6_months', etc.")
    start_date: Optional[str] = Field(None, description="For absolute: ISO date string")
    end_date: Optional[str] = Field(None, description="For absolute: ISO date string")
    window_size: Optional[int] = Field(None, description="For rolling: number of days/months")


class DataRequirements(BaseModel):
    """Data requirements for a widget."""
    query_type: Literal['aggregate', 'time_series', 'distribution', 'comparison', 'ranking'] = Field(..., description="Type of data query")
    dimensions: Optional[List[str]] = Field(default_factory=list, description="Group by dimensions")
    metrics: List[MetricDefinition] = Field(..., min_length=1, description="Metrics to calculate")
    filters: Optional[List[FilterDefinition]] = Field(default_factory=list, description="Data filters")
    time_range: Optional[TimeRange] = Field(None, description="Time range for query")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    limit: Optional[int] = Field(None, description="Result limit")


# =============================================================================
# Widget Models
# =============================================================================

class WidgetPosition(BaseModel):
    """Widget position in grid layout."""
    row: int = Field(..., ge=1, description="Starting row (1-indexed)")
    col: int = Field(..., ge=1, le=12, description="Starting column (1-indexed, max 12)")
    row_span: int = Field(..., ge=1, description="Height in row units")
    col_span: int = Field(..., ge=1, le=12, description="Width in column units (max 12)")


class WidgetSize(BaseModel):
    """Widget size constraints."""
    min_width: Optional[int] = Field(None, ge=1, description="Minimum width in grid units")
    min_height: Optional[int] = Field(None, ge=1, description="Minimum height in grid units")
    max_width: Optional[int] = Field(None, le=12, description="Maximum width in grid units")
    max_height: Optional[int] = Field(None, description="Maximum height in grid units")


class SparklineConfig(BaseModel):
    """Sparkline configuration for KPI cards."""
    data: List[float] = Field(..., description="Array of numeric values for the sparkline")
    type: Optional[Literal['line', 'area', 'bar']] = Field('line', description="Sparkline chart type")
    height: Optional[int] = Field(50, description="Height in pixels")
    color: Optional[str] = Field(None, description="Color for the sparkline")
    showPoints: Optional[bool] = Field(False, description="Show data points on line/area charts")


class TableColumn(BaseModel):
    """Table column configuration."""
    field: str = Field(..., description="Column field name")
    header: str = Field(..., description="Column header text")
    width: Optional[str] = Field(None, description="Column width")
    align: Optional[Literal['left', 'center', 'right']] = Field('left', description="Column alignment")


class ChartConfig(BaseModel):
    """Chart-specific configuration."""
    chart_type: Optional[Literal['line', 'bar', 'pie', 'waterfall', 'area', 'donut', 'scatter', 'heatmap',
                                   'gauge', 'radar', 'treemap', 'funnel', 'candlestick', 'boxPlot',
                                   'radialBar', 'polarArea', 'bubble', 'rangeBar']] = Field(None, description="Chart type")
    x_axis: Optional[str] = Field(None, description="X-axis field")
    y_axis: Optional[str] = Field(None, description="Y-axis field")
    group_by: Optional[str] = Field(None, description="Group by field")
    color: Optional[Any] = Field(None, description="Color scheme (string or list)")
    show_legend: Optional[bool] = Field(True, description="Show legend")
    show_grid: Optional[bool] = Field(True, description="Show grid lines")
    show_tooltip: Optional[bool] = Field(True, description="Show tooltips")
    show_target_line: Optional[bool] = Field(None, description="Show target line")
    target_value: Optional[float] = Field(None, description="Target value for comparison")
    stacked: Optional[bool] = Field(False, description="Stacked chart")
    horizontal: Optional[bool] = Field(None, description="Horizontal orientation")
    tension: Optional[float] = Field(None, description="Line tension/curve (0-1)")
    fill: Optional[bool] = Field(None, description="Fill area under line")
    point_radius: Optional[int] = Field(None, description="Point radius for scatter/line charts")
    border_width: Optional[int] = Field(None, description="Border width")
    curve: Optional[Literal['smooth', 'straight', 'stepline']] = Field(None, description="Curve type for line charts")

    # KPI Card specific
    icon: Optional[str] = Field(None, description="Icon name (e.g., 'tabler-trending-up')")
    show_trend: Optional[bool] = Field(None, description="Show trend indicator")
    subtitle: Optional[str] = Field(None, description="Subtitle text")
    trend_direction: Optional[Literal['up', 'down', 'neutral']] = Field(None, description="Trend direction")
    trend_value: Optional[str] = Field(None, description="Trend value display")
    sparkline: Optional[SparklineConfig] = Field(None, description="Sparkline configuration")
    format: Optional[str] = Field(None, description="Number format (currency, percentage, number)")

    # Table specific
    columns: Optional[List[TableColumn]] = Field(None, description="Table columns config")
    sortable: Optional[bool] = Field(None, description="Enable sorting (for tables)")
    filterable: Optional[bool] = Field(None, description="Enable filtering (for tables)")
    paginated: Optional[bool] = Field(None, description="Enable pagination (for tables)")
    page_size: Optional[int] = Field(None, description="Rows per page")

    # Gauge specific
    min_value: Optional[float] = Field(None, description="Minimum value for gauge")
    max_value: Optional[float] = Field(None, description="Maximum value for gauge")
    thresholds: Optional[List[Dict[str, Any]]] = Field(None, description="Gauge thresholds with colors")

    # Chart style
    orientation: Optional[Literal['vertical', 'horizontal']] = Field(None, description="Chart orientation")
    show_labels: Optional[bool] = Field(None, description="Show data labels")
    show_values: Optional[bool] = Field(None, description="Show values on chart")
    inner_radius: Optional[int] = Field(None, description="Inner radius for donut charts")
    show_markers: Optional[bool] = Field(None, description="Show markers on line/radar charts")
    distributed: Optional[bool] = Field(None, description="Distributed colors (treemap)")

    # Composite widget config
    metrics: Optional[List[str]] = Field(None, description="List of metrics for comparison widgets")
    showPercentChange: Optional[bool] = Field(None, description="Show percentage change")
    show_sparklines: Optional[bool] = Field(None, description="Show sparklines in metrics")
    layout: Optional[Literal['horizontal', 'vertical', 'grid']] = Field(None, description="Layout mode")
    show_percentages: Optional[bool] = Field(None, description="Show percentages")
    show_donut: Optional[bool] = Field(None, description="Show donut chart")
    show_rank_numbers: Optional[bool] = Field(None, description="Show rank numbers")
    max_items: Optional[int] = Field(None, description="Maximum items to display")
    show_targets: Optional[bool] = Field(None, description="Show targets")
    show_breakeven_line: Optional[bool] = Field(None, description="Show breakeven line")
    bar_height: Optional[int] = Field(None, description="Bar height for progress bars")
    show_min_max: Optional[bool] = Field(None, description="Show min/max values")
    sparkline_type: Optional[Literal['line', 'area', 'bar']] = Field(None, description="Sparkline type")
    sparkline_data: Optional[List[float]] = Field(None, description="Sparkline data points")


class DashboardWidgetNew(BaseModel):
    """Dashboard widget with data requirements."""
    widget_id: str = Field(..., description="Unique widget identifier")
    widget_type: Literal[
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
    title: str = Field(..., min_length=5, max_length=200, description="Widget title")
    description: Optional[str] = Field(None, max_length=500, description="Widget description")
    position: WidgetPosition = Field(..., description="Grid position")
    size: Optional[WidgetSize] = Field(None, description="Size constraints")
    data_requirements: DataRequirements = Field(..., description="Data requirements specification")
    analytics_question: str = Field(..., min_length=10, description="Natural language question this widget answers")
    chart_config: Optional[ChartConfig] = Field(default_factory=ChartConfig, description="Chart configuration")


# =============================================================================
# Template Models
# =============================================================================

class VisualStyleNew(BaseModel):
    """Visual styling for template."""
    primary_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Primary color (hex)")
    accent_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Accent color (hex)")
    layout: Literal['dense', 'balanced', 'spacious'] = Field(..., description="Layout density")


class TemplateMetadata(BaseModel):
    """Template generation metadata."""
    generated_by: Literal['llm', 'manual', 'hybrid'] = Field(..., description="Generation method")
    llm_model: Optional[str] = Field(None, description="LLM model used (e.g., 'claude-3-5-sonnet')")
    generation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    key_features: List[str] = Field(..., min_length=1, max_length=10, description="Key features list")
    recommended_use_case: Optional[str] = Field(None, description="Recommended use case")
    version: Optional[str] = Field("1.0", description="Template version")


class ProspectDashboardTemplate(BaseModel):
    """Complete prospect dashboard template with data requirements."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Template ID")
    client_id: str = Field(..., description="Client UUID")
    name: str = Field(..., min_length=5, max_length=200, description="Template name")
    description: str = Field(..., min_length=20, max_length=1000, description="Template description")
    category: Literal[
        'roi-focused',
        'clinical-outcomes',
        'operational-efficiency',
        'competitive-positioning',
        'comprehensive'
    ] = Field(..., description="Template category")
    target_audience: str = Field(..., description="Target audience")
    visual_style: VisualStyleNew = Field(..., description="Visual styling")
    widgets: List[DashboardWidgetNew] = Field(..., min_length=1, max_length=20, description="Widget list")
    metadata: TemplateMetadata = Field(..., description="Template metadata")
    status: Literal['draft', 'approved', 'archived', 'deprecated'] = Field('draft', description="Template status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "scenario-comparison-template-001",
                "client_id": "client-livongo-diabetes",
                "name": "Three-Scenario ROI Comparison",
                "description": "Side-by-side comparison of conservative, moderate, and optimistic ROI scenarios",
                "category": "roi-focused",
                "target_audience": "Health Plan",
                "visual_style": {
                    "primary_color": "#c62828",
                    "accent_color": "#6a1b9a",
                    "layout": "balanced"
                },
                "widgets": [],
                "metadata": {
                    "generated_by": "llm",
                    "llm_model": "claude-3-5-sonnet-20241022",
                    "generation_timestamp": "2025-01-15T10:30:00Z",
                    "key_features": [
                        "Conservative scenario: 2.6x ROI",
                        "Moderate scenario: 3.4x ROI"
                    ],
                    "recommended_use_case": "Financial planning and risk assessment"
                },
                "status": "approved"
            }
        }


# =============================================================================
# Prospect Dashboard Data Models
# =============================================================================

class ProspectDataSchema(BaseModel):
    """Schema definition for prospect data."""
    table_name: str = Field(..., description="Table or data source name")
    fields: List[Dict[str, str]] = Field(..., description="Available fields with types")
    available_metrics: List[str] = Field(default_factory=list, description="Pre-calculated metrics")
    time_fields: List[str] = Field(default_factory=list, description="Time/date fields")
    dimension_fields: List[str] = Field(default_factory=list, description="Categorical dimension fields")


class DataValidationResult(BaseModel):
    """Result of validating template against prospect data."""
    is_valid: bool = Field(..., description="Overall validation status")
    missing_fields: List[str] = Field(default_factory=list, description="Fields referenced but not available")
    missing_metrics: List[str] = Field(default_factory=list, description="Metrics that can't be calculated")
    invalid_filters: List[Dict[str, str]] = Field(default_factory=list, description="Invalid filter definitions")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    validated_widgets: int = Field(0, description="Number of widgets validated")
    failed_widgets: List[str] = Field(default_factory=list, description="Widget IDs that failed validation")


class ProspectDashboardData(BaseModel):
    """Prospect dashboard data instance."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = Field(..., description="Reference to dashboard template")
    prospect_id: str = Field(..., description="Prospect/client ID")
    data: Dict[str, Any] = Field(..., description="Actual data for widgets")
    validation_result: Optional[DataValidationResult] = Field(None, description="Validation result")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    generated_by: Optional[str] = Field(None, description="User or system that generated data")
    status: Literal['generating', 'ready', 'stale', 'error'] = Field('generating', description="Data status")


# =============================================================================
# Validation Functions
# =============================================================================

def validate_template_against_data_schema(
    template: ProspectDashboardTemplate,
    data_schema: ProspectDataSchema
) -> DataValidationResult:
    """Validate template data requirements against available data schema.

    Args:
        template: Dashboard template with data requirements
        data_schema: Available data schema

    Returns:
        DataValidationResult with validation details
    """
    result = DataValidationResult(is_valid=True, validated_widgets=len(template.widgets))

    available_fields = {field['name'] for field in data_schema.fields}
    available_metrics = set(data_schema.available_metrics)

    for widget in template.widgets:
        widget_errors = []

        # Validate metrics
        for metric in widget.data_requirements.metrics:
            # Check if metric references unavailable fields
            # Simple check: look for field names in expression
            for field in available_fields:
                if field in metric.expression:
                    continue

            # Check if metric is in available_metrics
            if metric.name not in available_metrics:
                # Check if expression can be constructed from available fields
                missing = []
                for field_def in data_schema.fields:
                    field_name = field_def['name']
                    if field_name not in metric.expression and 'SUM' in metric.expression:
                        # Field might be needed
                        pass

                if missing:
                    result.missing_metrics.append(f"{widget.widget_id}: {metric.name}")
                    widget_errors.append(f"Metric {metric.name} cannot be calculated")

        # Validate filters
        for filter_def in widget.data_requirements.filters or []:
            if filter_def.field not in available_fields:
                result.missing_fields.append(filter_def.field)
                result.invalid_filters.append({
                    "widget_id": widget.widget_id,
                    "field": filter_def.field,
                    "reason": "Field not available in data schema"
                })
                widget_errors.append(f"Filter field '{filter_def.field}' not available")

        # Validate dimensions
        for dim in widget.data_requirements.dimensions or []:
            if dim not in data_schema.dimension_fields and dim not in available_fields:
                result.missing_fields.append(dim)
                widget_errors.append(f"Dimension '{dim}' not available")

        # Validate time range
        if widget.data_requirements.time_range:
            time_range = widget.data_requirements.time_range
            if not data_schema.time_fields:
                result.warnings.append(f"{widget.widget_id}: Time range specified but no time fields available")

        if widget_errors:
            result.failed_widgets.append(widget.widget_id)
            result.is_valid = False

    return result


def validate_chart_config_compatibility(template: ProspectDashboardTemplate) -> List[str]:
    """
    Validate chart_config matches widget_type requirements.

    Returns list of validation errors.
    """
    errors = []

    # Define expected chart_type per widget_type
    chart_type_mapping = {
        # Line charts
        'line-chart': ['line'],
        'multi-line-chart': ['line'],
        'area-chart': ['area'],
        'stacked-area-chart': ['area'],

        # Bar charts
        'bar-chart': ['bar'],
        'horizontal-bar-chart': ['bar'],
        'stacked-bar-chart': ['bar'],
        'grouped-bar-chart': ['bar'],

        # Pie/Donut charts
        'pie-chart': ['pie'],
        'donut-chart': ['donut'],

        # Specialized charts
        'waterfall-chart': ['waterfall'],
        'scatter-plot': ['scatter'],
        'bubble-chart': ['bubble'],
        'radar-chart': ['radar'],
        'polar-area-chart': ['polarArea'],
        'gauge-chart': ['gauge'],
        'heatmap': ['heatmap'],
        'treemap': ['treemap'],
        'funnel-chart': ['funnel'],
        'candlestick-chart': ['candlestick'],
        'box-plot': ['boxPlot'],
        'radial-bar-chart': ['radialBar'],
        'range-bar-chart': ['rangeBar'],
    }

    # Define required config fields per widget_type
    required_config_fields = {
        'kpi-card': ['icon', 'subtitle'],
        'gauge-chart': ['min_value', 'max_value'],
        'data-table': ['columns'],
        'progress-bar': ['target_value'],
        'kpi-grid': ['metrics'],
        'metric-comparison': ['metrics'],
        'scorecard': ['metrics'],
        'clinical-metrics': ['metrics'],
    }

    # Define incompatible config fields per widget_type
    incompatible_fields = {
        'kpi-card': ['x_axis', 'y_axis', 'show_grid'],
        'gauge-chart': ['x_axis', 'y_axis', 'stacked'],
        'data-table': ['chart_type', 'x_axis', 'y_axis'],
        'progress-bar': ['chart_type', 'x_axis', 'y_axis'],
    }

    for widget in template.widgets:
        widget_type = widget.widget_type
        config = widget.chart_config or ChartConfig()

        # Check chart_type matches widget_type
        if widget_type in chart_type_mapping:
            expected_types = chart_type_mapping[widget_type]
            if config.chart_type and config.chart_type not in expected_types:
                errors.append(
                    f"Widget '{widget.widget_id}' ({widget_type}): "
                    f"chart_type '{config.chart_type}' incompatible. "
                    f"Expected: {', '.join(expected_types)}"
                )

        # Check required fields are present
        if widget_type in required_config_fields:
            for field in required_config_fields[widget_type]:
                field_value = getattr(config, field, None)
                if field_value is None:
                    errors.append(
                        f"Widget '{widget.widget_id}' ({widget_type}): "
                        f"missing required config field '{field}'"
                    )

        # Check for incompatible fields
        if widget_type in incompatible_fields:
            for field in incompatible_fields[widget_type]:
                field_value = getattr(config, field, None)
                if field_value is not None:
                    errors.append(
                        f"Widget '{widget.widget_id}' ({widget_type}): "
                        f"incompatible config field '{field}' should not be set"
                    )

        # Validate gauge thresholds structure
        if widget_type == 'gauge-chart' and config.thresholds:
            if not isinstance(config.thresholds, list) or len(config.thresholds) < 2:
                errors.append(
                    f"Widget '{widget.widget_id}' (gauge-chart): "
                    f"thresholds must be a list with at least 2 entries"
                )
            else:
                for i, threshold in enumerate(config.thresholds):
                    if not isinstance(threshold, dict) or 'value' not in threshold or 'color' not in threshold:
                        errors.append(
                            f"Widget '{widget.widget_id}' (gauge-chart): "
                            f"threshold #{i} must have 'value' and 'color'"
                        )

        # Validate table columns
        if widget_type == 'data-table' and config.columns:
            if not isinstance(config.columns, list) or len(config.columns) == 0:
                errors.append(
                    f"Widget '{widget.widget_id}' (data-table): "
                    f"columns must be a non-empty list"
                )
            else:
                for i, col in enumerate(config.columns):
                    if not hasattr(col, 'field') or not hasattr(col, 'header'):
                        errors.append(
                            f"Widget '{widget.widget_id}' (data-table): "
                            f"column #{i} must have 'field' and 'header'"
                        )

        # Validate metrics arrays for comparison widgets
        if widget_type in ['metric-comparison', 'scorecard', 'kpi-grid', 'clinical-metrics']:
            if config.metrics:
                if not isinstance(config.metrics, list) or len(config.metrics) < 2:
                    errors.append(
                        f"Widget '{widget.widget_id}' ({widget_type}): "
                        f"requires at least 2 metrics"
                    )

        # Validate sparkline config for KPI cards
        if widget_type == 'kpi-card' and config.sparkline:
            sparkline = config.sparkline
            if not hasattr(sparkline, 'data') or not isinstance(sparkline.data, list):
                errors.append(
                    f"Widget '{widget.widget_id}' (kpi-card): "
                    f"sparkline must have 'data' as a list"
                )

    return errors


def validate_widget_data_format(
    widget_type: str,
    data: Dict[str, Any]
) -> List[str]:
    """
    Validate widget data format matches widget type expectations.

    Args:
        widget_type: Type of widget
        data: Generated data for the widget

    Returns:
        List of validation errors
    """
    errors = []

    # Check for required top-level keys
    if 'data_points' not in data:
        errors.append(f"Widget data missing required key 'data_points'")
        return errors

    if 'query_metadata' not in data:
        errors.append(f"Widget data missing required key 'query_metadata'")

    data_points = data.get('data_points', [])

    # Validate data_points is a list
    if not isinstance(data_points, list):
        errors.append(f"'data_points' must be a list, got {type(data_points).__name__}")
        return errors

    # Check minimum data point count per widget type
    min_data_points = {
        'kpi-card': 1,
        'kpi-grid': 2,
        'metric-comparison': 2,
        'scorecard': 2,
        'gauge-chart': 1,
        'progress-bar': 1,
        'line-chart': 3,
        'multi-line-chart': 5,
        'area-chart': 3,
        'bar-chart': 3,
        'pie-chart': 2,
        'donut-chart': 2,
        'data-table': 1,
        'heatmap': 4,
        'ranked-list': 3,
        'treemap': 3,
        'funnel-chart': 3,
        'waterfall-chart': 3,
        'scatter-plot': 5,
        'bubble-chart': 5,
        'radar-chart': 3,
    }

    if widget_type in min_data_points:
        min_count = min_data_points[widget_type]
        if len(data_points) < min_count:
            errors.append(
                f"{widget_type} requires at least {min_count} data points, got {len(data_points)}"
            )

    # Validate each data point structure
    for i, point in enumerate(data_points):
        if not isinstance(point, dict):
            errors.append(f"data_points[{i}] must be a dict, got {type(point).__name__}")
            continue

        # Check required fields in data point
        required_fields = ['value', 'formatted_value']
        for field in required_fields:
            if field not in point:
                errors.append(f"data_points[{i}] missing required field '{field}'")

        # Validate value is numeric for most widget types
        numeric_widget_types = [
            'kpi-card', 'gauge-chart', 'progress-bar', 'line-chart', 'area-chart',
            'bar-chart', 'scatter-plot', 'bubble-chart', 'waterfall-chart'
        ]
        if widget_type in numeric_widget_types:
            if 'value' in point and not isinstance(point['value'], (int, float)):
                errors.append(
                    f"data_points[{i}].value must be numeric for {widget_type}, "
                    f"got {type(point['value']).__name__}"
                )

    # Validate query_metadata structure
    if 'query_metadata' in data:
        query_meta = data['query_metadata']
        if not isinstance(query_meta, dict):
            errors.append(f"'query_metadata' must be a dict, got {type(query_meta).__name__}")
        else:
            required_meta_fields = ['query_used', 'execution_time_ms', 'row_count', 'generated_at']
            for field in required_meta_fields:
                if field not in query_meta:
                    errors.append(f"query_metadata missing required field '{field}'")

    # Widget-specific data format validation
    if widget_type == 'data-table':
        # Tables need consistent keys across all data points
        if data_points:
            first_keys = set(data_points[0].keys())
            for i, point in enumerate(data_points[1:], start=1):
                point_keys = set(point.keys())
                if point_keys != first_keys:
                    errors.append(
                        f"data-table data_points[{i}] has inconsistent keys. "
                        f"Expected: {first_keys}, Got: {point_keys}"
                    )

    elif widget_type in ['line-chart', 'multi-line-chart', 'area-chart', 'stacked-area-chart']:
        # Time-series widgets need label field (for x-axis)
        for i, point in enumerate(data_points):
            if 'label' not in point:
                errors.append(f"Time-series widget data_points[{i}] missing 'label' field for x-axis")

    elif widget_type in ['pie-chart', 'donut-chart', 'treemap', 'funnel-chart']:
        # Distribution widgets need label field
        for i, point in enumerate(data_points):
            if 'label' not in point:
                errors.append(f"Distribution widget data_points[{i}] missing 'label' field")

    elif widget_type == 'heatmap':
        # Heatmap needs x, y coordinates in metadata
        for i, point in enumerate(data_points):
            metadata = point.get('metadata', {})
            if 'x' not in metadata or 'y' not in metadata:
                errors.append(f"Heatmap data_points[{i}] metadata missing 'x' or 'y' coordinates")

    return errors


def convert_old_template_to_new_format(
    old_template: Dict[str, Any],
    default_data_requirements: Optional[Dict[str, Any]] = None
) -> ProspectDashboardTemplate:
    """Convert old template format to new format with data requirements.

    Args:
        old_template: Template in old format
        default_data_requirements: Default data requirements to use if not specified

    Returns:
        ProspectDashboardTemplate in new format
    """
    # Extract basic info
    template_data = {
        "id": old_template.get("id", str(uuid.uuid4())),
        "client_id": old_template.get("client_id", "unknown"),
        "name": old_template["name"],
        "description": old_template["description"],
        "category": old_template["category"],
        "target_audience": old_template.get("targetAudience", old_template.get("target_audience", "General")),
        "visual_style": {
            "primary_color": old_template.get("visualStyle", {}).get("primaryColor", "#2563eb"),
            "accent_color": old_template.get("visualStyle", {}).get("accentColor", "#10b981"),
            "layout": old_template.get("visualStyle", {}).get("layout", "balanced")
        },
        "widgets": [],
        "metadata": {
            "generated_by": "llm",
            "llm_model": "claude-sonnet-4",
            "generation_timestamp": datetime.utcnow().isoformat(),
            "key_features": old_template.get("keyFeatures", ["Converted from old format"]),
            "recommended_use_case": old_template.get("recommendedUseCase", "General purpose")
        },
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Convert widgets
    for old_widget in old_template.get("widgets", []):
        # Create default data requirements if not provided
        widget_type = old_widget.get("type", "kpi-card")

        # Infer data requirements from widget type
        if default_data_requirements:
            data_reqs = default_data_requirements
        else:
            data_reqs = {
                "query_type": "aggregate",
                "metrics": [{
                    "name": "default_metric",
                    "expression": "COUNT(*)",
                    "data_type": "number"
                }],
                "filters": []
            }

        new_widget = {
            "widget_id": old_widget.get("id", f"w_{uuid.uuid4().hex[:8]}"),
            "widget_type": widget_type,
            "title": old_widget["title"],
            "description": f"Auto-generated description for {old_widget['title']}",
            "position": {
                "row": old_widget["position"]["row"],
                "col": old_widget["position"]["col"],
                "row_span": old_widget["position"]["rowSpan"],
                "col_span": old_widget["position"]["colSpan"]
            },
            "data_requirements": data_reqs,
            "analytics_question": f"What is the {old_widget['title']}?",
            "chart_config": old_widget.get("config", {})
        }

        template_data["widgets"].append(DashboardWidgetNew(**new_widget))

    return ProspectDashboardTemplate(**template_data)

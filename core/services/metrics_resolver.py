"""
Metrics Resolver Service

Resolves metric references from data_requirements to actual SQL expressions.
Supports both library metric references and custom expressions.
"""

from typing import Dict, Any, Optional
from core.models.metrics_library import METRICS_LIBRARY, get_metric
from core.models.template_models import MetricDefinition
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


def resolve_metric(metric_def: MetricDefinition) -> Dict[str, Any]:
    """
    Resolve a metric definition to its SQL expression and metadata.

    Args:
        metric_def: MetricDefinition from data_requirements

    Returns:
        Dict with resolved expression, data_type, format, and metadata

    Raises:
        ValueError: If metric cannot be resolved
    """
    # Case 1: Metric reference to library
    if metric_def.metric_ref:
        try:
            library_metric = get_metric(metric_def.metric_ref)

            return {
                "name": metric_def.name,
                "expression": library_metric["expression"],
                "data_type": metric_def.data_type,
                "format": metric_def.format,
                "source": "library",
                "metric_ref": metric_def.metric_ref,
                "required_tables": library_metric.get("required_tables", []),
                "description": library_metric.get("description", "")
            }

        except KeyError as e:
            logger.error(f"Metric reference '{metric_def.metric_ref}' not found in library")
            raise ValueError(f"Invalid metric reference: {metric_def.metric_ref}") from e

    # Case 2: Custom SQL expression
    elif metric_def.expression:
        return {
            "name": metric_def.name,
            "expression": metric_def.expression,
            "data_type": metric_def.data_type,
            "format": metric_def.format,
            "source": "custom",
            "metric_ref": None,
            "required_tables": _extract_tables_from_expression(metric_def.expression),
            "description": f"Custom metric: {metric_def.name}"
        }

    # Case 3: Neither provided - error
    else:
        raise ValueError(
            f"Metric '{metric_def.name}' must have either 'metric_ref' or 'expression'"
        )


def _extract_tables_from_expression(expression: str) -> list:
    """
    Extract table names from SQL expression.

    Simple heuristic: looks for common table names in expression.
    More sophisticated parsing would use SQL parser.

    Args:
        expression: SQL expression string

    Returns:
        List of likely table names
    """
    known_tables = [
        "enrollments",
        "clinical_outcomes",
        "financial_outcomes",
        "utilization",
        "member_engagement",
        "quality_measures",
        "complications"
    ]

    tables_found = []
    expression_lower = expression.lower()

    for table in known_tables:
        if table in expression_lower:
            tables_found.append(table)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(tables_found))


def resolve_all_metrics(metric_defs: list[MetricDefinition]) -> list[Dict[str, Any]]:
    """
    Resolve all metrics in a list.

    Args:
        metric_defs: List of MetricDefinition objects

    Returns:
        List of resolved metric dictionaries

    Raises:
        ValueError: If any metric fails to resolve
    """
    resolved = []

    for metric_def in metric_defs:
        try:
            resolved_metric = resolve_metric(metric_def)
            resolved.append(resolved_metric)
            logger.debug(f"Resolved metric '{metric_def.name}' from {resolved_metric['source']}")

        except ValueError as e:
            logger.error(f"Failed to resolve metric '{metric_def.name}': {e}")
            raise

    return resolved


def get_required_tables(resolved_metrics: list[Dict[str, Any]]) -> list[str]:
    """
    Get all required tables from resolved metrics.

    Args:
        resolved_metrics: List of resolved metric dictionaries

    Returns:
        Deduplicated list of required table names
    """
    all_tables = []

    for metric in resolved_metrics:
        all_tables.extend(metric.get("required_tables", []))

    # Remove duplicates while preserving order
    return list(dict.fromkeys(all_tables))

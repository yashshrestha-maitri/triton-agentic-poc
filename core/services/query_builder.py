"""
Query Builder Service

Builds SQL queries from data_requirements specifications.
Converts metric expressions, filters, and dimensions into executable SQL.
"""

from typing import Dict, Any, List, Optional
from core.models.template_models import DataRequirements, FilterDefinition
from core.services.metrics_resolver import resolve_all_metrics, get_required_tables
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


def build_query(data_requirements: DataRequirements) -> Dict[str, Any]:
    """
    Build SQL query from data_requirements specification.

    Args:
        data_requirements: DataRequirements object from widget

    Returns:
        Dict with query_sql, required_tables, query_type, and metadata

    Raises:
        ValueError: If query cannot be built
    """
    if not data_requirements.metrics or len(data_requirements.metrics) == 0:
        raise ValueError("data_requirements must have at least one metric")

    # Step 1: Resolve all metrics to SQL expressions
    resolved_metrics = resolve_all_metrics(data_requirements.metrics)

    # Step 2: Build SELECT clause
    select_clause = _build_select_clause(resolved_metrics, data_requirements.dimensions)

    # Step 3: Determine required tables
    required_tables = get_required_tables(resolved_metrics)

    # Step 4: Build FROM clause
    from_clause = _build_from_clause(required_tables)

    # Step 5: Build WHERE clause (if filters exist)
    where_clause = _build_where_clause(data_requirements.filters) if data_requirements.filters else ""

    # Step 6: Build GROUP BY clause (if dimensions exist)
    group_by_clause = _build_group_by_clause(data_requirements.dimensions) if data_requirements.dimensions else ""

    # Step 7: Build ORDER BY clause (for time-series)
    order_by_clause = _build_order_by_clause(data_requirements.query_type, data_requirements.dimensions)

    # Step 8: Assemble complete query
    query_parts = [f"SELECT {select_clause}", f"FROM {from_clause}"]

    if where_clause:
        query_parts.append(f"WHERE {where_clause}")

    if group_by_clause:
        query_parts.append(f"GROUP BY {group_by_clause}")

    if order_by_clause:
        query_parts.append(f"ORDER BY {order_by_clause}")

    query_sql = "\n".join(query_parts)

    return {
        "query_sql": query_sql,
        "required_tables": required_tables,
        "query_type": data_requirements.query_type,
        "metrics": resolved_metrics,
        "has_filters": bool(data_requirements.filters),
        "has_grouping": bool(data_requirements.dimensions),
        "has_time_range": bool(data_requirements.time_range)
    }


def _build_select_clause(resolved_metrics: List[Dict[str, Any]], dimensions: Optional[List[str]] = None) -> str:
    """Build SELECT clause from resolved metrics and dimensions."""
    select_parts = []

    # Add dimensions first (for GROUP BY)
    if dimensions:
        select_parts.extend(dimensions)

    # Add metric expressions
    for metric in resolved_metrics:
        metric_expr = f"{metric['expression']} AS {metric['name']}"
        select_parts.append(metric_expr)

    return ", ".join(select_parts)


def _build_from_clause(required_tables: List[str]) -> str:
    """
    Build FROM clause with appropriate JOINs.

    For simplicity, we use the first table and LEFT JOIN others on member_id.
    More sophisticated logic could analyze relationships.
    """
    if not required_tables:
        raise ValueError("At least one table must be specified")

    if len(required_tables) == 1:
        return required_tables[0]

    # Use first table as base
    base_table = required_tables[0]
    from_parts = [base_table]

    # LEFT JOIN other tables on member_id
    for table in required_tables[1:]:
        from_parts.append(f"LEFT JOIN {table} ON {base_table}.member_id = {table}.member_id")

    return "\n".join(from_parts)


def _build_where_clause(filters: List[FilterDefinition]) -> str:
    """Build WHERE clause from filter definitions."""
    if not filters:
        return ""

    filter_conditions = []

    for f in filters:
        condition = _build_filter_condition(f)
        filter_conditions.append(condition)

    return " AND ".join(filter_conditions)


def _build_filter_condition(filter_def: FilterDefinition) -> str:
    """Build a single filter condition."""
    field = filter_def.field
    operator = filter_def.operator
    value = filter_def.value

    # Map operators to SQL
    operator_map = {
        'eq': '=',
        'ne': '!=',
        'gt': '>',
        'lt': '<',
        'gte': '>=',
        'lte': '<=',
        'in': 'IN',
        'like': 'LIKE'
    }

    sql_operator = operator_map.get(operator, '=')

    # Handle different value types
    if operator == 'in':
        if isinstance(value, list):
            quoted_values = [f"'{v}'" if isinstance(v, str) else str(v) for v in value]
            return f"{field} IN ({', '.join(quoted_values)})"
        else:
            return f"{field} = '{value}'"

    elif operator == 'between':
        if isinstance(value, list) and len(value) == 2:
            return f"{field} BETWEEN {value[0]} AND {value[1]}"
        else:
            raise ValueError(f"BETWEEN operator requires list of 2 values, got: {value}")

    elif isinstance(value, str):
        return f"{field} {sql_operator} '{value}'"

    else:
        return f"{field} {sql_operator} {value}"


def _build_group_by_clause(dimensions: Optional[List[str]]) -> str:
    """Build GROUP BY clause from dimensions."""
    if not dimensions:
        return ""

    return ", ".join(dimensions)


def _build_order_by_clause(query_type: str, dimensions: Optional[List[str]]) -> str:
    """Build ORDER BY clause based on query type."""
    # For time-series, order by first dimension (usually time)
    if query_type == "time-series" and dimensions:
        return dimensions[0]

    # For others, no specific ordering
    return ""


def generate_query_metadata(query_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate query metadata for inclusion in widget data.

    Args:
        query_result: Result from build_query()

    Returns:
        Dict with query_used, execution_time_ms, etc.
    """
    return {
        "query_used": query_result["query_sql"],
        "query_type": query_result["query_type"],
        "required_tables": query_result["required_tables"],
        "metrics_count": len(query_result["metrics"]),
        "has_filters": query_result["has_filters"],
        "has_grouping": query_result["has_grouping"]
    }

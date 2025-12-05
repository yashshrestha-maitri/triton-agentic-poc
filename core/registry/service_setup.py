"""Utility for setting up Mare service features."""

from typing import Any, Callable, Optional
from core.monitoring.logger import get_logger

logger = get_logger(__name__)


def setup_mare_service(
    instance: Any,
    service_type: str,
    register_func: Callable,
    initialized_attr: str,
    service_info_attr: str
) -> Any:
    """Set up Mare-specific features for a service instance.

    Args:
        instance: The service instance to set up
        service_type: Type of service (e.g., 'agent', 'tool')
        register_func: Function to call for registration
        initialized_attr: Name of the attribute to check/set for initialization
        service_info_attr: Name of the attribute to store service info

    Returns:
        ServiceInfo object or None
    """
    # Check if already initialized
    if getattr(instance, initialized_attr, False):
        logger.debug(f"{service_type.capitalize()} already initialized")
        return getattr(instance, service_info_attr, None)

    # Get service identifier
    service_id = getattr(instance, f'{service_type}_id', None) or \
                 getattr(instance, 'name', 'unknown')
    name = getattr(instance, 'name', 'Unknown')

    # Register the service
    try:
        service_info = register_func(service_id, name)
        setattr(instance, initialized_attr, True)
        logger.info(f"Registered {service_type}: {name} (ID: {service_id})")
        return service_info
    except Exception as e:
        logger.error(f"Failed to register {service_type} {name}: {e}")
        return None

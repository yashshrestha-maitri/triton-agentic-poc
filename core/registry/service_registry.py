"""Service registry for managing agent and service instances."""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ServiceStatus(Enum):
    """Service status enumeration."""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServiceInfo:
    """Information about a registered service."""

    def __init__(self, service_id: str, service_type: str, name: str):
        self.service_id = service_id
        self.service_type = service_type
        self.name = name
        self.status = ServiceStatus.INITIALIZING
        self.registered_at = datetime.utcnow()
        self.last_health_check = None
        self.metadata = {}

    def __dict__(self):
        return {
            'service_id': self.service_id,
            'service_type': self.service_type,
            'name': self.name,
            'status': self.status.value,
            'registered_at': self.registered_at.isoformat(),
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'metadata': self.metadata
        }


class ServiceRegistry:
    """Registry for tracking all services and agents."""

    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}

    def register(self, service_id: str, service_type: str, name: str) -> ServiceInfo:
        """Register a new service."""
        service_info = ServiceInfo(service_id, service_type, name)
        self._services[service_id] = service_info
        return service_info

    def get(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service info by ID."""
        return self._services.get(service_id)

    def update_status(self, service_id: str, status: ServiceStatus):
        """Update service status."""
        if service_id in self._services:
            self._services[service_id].status = status
            self._services[service_id].last_health_check = datetime.utcnow()

    def get_all(self) -> Dict[str, ServiceInfo]:
        """Get all registered services."""
        return self._services.copy()


# Global service registry instance
service_registry = ServiceRegistry()


def register_agent_service(agent_id: str, name: str) -> ServiceInfo:
    """Register an agent service."""
    return service_registry.register(agent_id, "agent", name)

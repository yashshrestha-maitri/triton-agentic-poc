"""Celery tasks for Triton Agentic."""

from tasks.template_generation import generate_templates_task

__all__ = ["generate_templates_task"]

"""Structured logging configuration."""

import logging
from typing import Any

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=None,
        level=level,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        A structlog bound logger
    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding structured logging context."""

    def __init__(self, **context: Any) -> None:
        """Initialize logging context.
        
        Args:
            **context: Key-value pairs to add to logs
        """
        self.context = context
        self.logger = structlog.get_logger()

    def __enter__(self) -> None:
        """Enter context manager."""
        self.logger = self.logger.bind(**self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.logger = self.logger.unbind(*self.context.keys())

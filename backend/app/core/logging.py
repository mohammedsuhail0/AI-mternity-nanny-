import logging
import structlog
from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    structlog.configure(
        processors=shared_processors + [structlog.processors.JSONRenderer()],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        handlers=[logging.StreamHandler()],
    )

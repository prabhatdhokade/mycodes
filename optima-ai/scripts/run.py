"""Entrypoint script for running the Optima AI server."""

import uvicorn

from optima_ai.core.config import get_settings


def main():
    settings = get_settings()
    uvicorn.run(
        "optima_ai.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()

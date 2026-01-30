import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import (
    CollectorRegistry,
    Counter,
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
)

from app.api import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan контекст для управления жизненным циклом приложения"""
    registry = CollectorRegistry()
    registry.register(GC_COLLECTOR)
    registry.register(PLATFORM_COLLECTOR)
    registry.register(PROCESS_COLLECTOR)
    app.state.system_metrics_registry = registry

    registry = CollectorRegistry()
    app.state.feels_like_counter = Counter(
        name="temp_feels_like",
        documentation="Description of counter",
        labelnames=["feels_like"],
        registry=registry,
    )
    app.state.analytic_metrics_registry = registry

    logger.info("Metrics collectors initialized")
    yield
    logger.info("Metrics collectors shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(router)

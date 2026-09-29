from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from lexagent.api.middleware import MaxBodySizeMiddleware
from lexagent.api.rate_limit import limiter
from lexagent.api.routes import ask, health, queries
from lexagent.observability import configure_logging
from lexagent.settings import get_settings

settings = get_settings()
configure_logging(settings.environment)

app = FastAPI(title="LexAgent", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(MaxBodySizeMiddleware, max_body_bytes=settings.max_request_body_bytes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ask.router)
app.include_router(queries.router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "service": "LexAgent API",
        "ui": "http://localhost:3000 (start with `make run`)",
        "docs": "/docs",
    }

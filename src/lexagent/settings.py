from functools import lru_cache

from pydantic_settings import SettingsConfigDict
from zarreh_agentkit.settings import AgentSettings


class Settings(AgentSettings):
    """Application configuration, sourced from the environment."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEXAGENT_", extra="ignore")

    langsmith_project: str = "lexagent"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "lexagent"
    qdrant_api_key: str = ""

    statute_collection: str = "lexagent_statutes"
    precedent_collection: str = "lexagent_precedents"

    run_store_path: str = "data/runs.db"
    max_request_body_bytes: int = 2 * 1024 * 1024  # 2 MiB


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Configuration loaded from environment variables."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "healthmap-ai-agent-service"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    port: int = Field(default=8000, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    llm_model: str = Field(default="gemini-2.5-flash", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, alias="LLM_TEMPERATURE")
    embedding_model: str = Field(default="gemini-embedding-001", alias="EMBEDDING_MODEL")

    pinecone_api_key: str = Field(default="", alias="PINECONE_API_KEY")
    pinecone_index_name: str = Field(default="healthmap-clinical", alias="PINECONE_INDEX_NAME")
    pinecone_environment: str = Field(default="us-east-1", alias="PINECONE_ENVIRONMENT")

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")

    patient_service_url: str = Field(default="http://patient-service:8080", alias="PATIENT_SERVICE_URL")
    lab_service_url: str = Field(default="http://lab-service:8080", alias="LAB_SERVICE_URL")
    medication_service_url: str = Field(default="http://medication-service:8080", alias="MEDICATION_SERVICE_URL")

    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    max_concurrent_agents: int = Field(default=10, alias="MAX_CONCURRENT_AGENTS")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    youtube_api_key: str | None = os.getenv("YOUTUBE_API_KEY")
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()

    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # IBM watsonx
    watsonx_url: str | None = os.getenv("WATSONX_URL")
    watsonx_apikey: str | None = os.getenv("WATSONX_APIKEY")
    watsonx_project_id: str | None = os.getenv("WATSONX_PROJECT_ID")
    watsonx_model_id: str = os.getenv("WATSONX_MODEL_ID", "mistralai/mistral-small-3-1-24b-instruct-2503")

settings = Settings()
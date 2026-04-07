from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    model: str = os.getenv("SMARTLEARN_MODEL", "gpt-5.4-mini")
    app_title: str = os.getenv(
        "SMARTLEARN_APP_TITLE", "SmartLearn: Multi-Agent Learning System"
    )
    max_reference_snippets: int = int(os.getenv("SMARTLEARN_MAX_REFERENCE_SNIPPETS", "3"))
    reference_chunk_chars: int = int(os.getenv("SMARTLEARN_REFERENCE_CHUNK_CHARS", "1000"))

    def validate(self) -> None:
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Create a .env file or export the key in your shell."
            )


settings = Settings()

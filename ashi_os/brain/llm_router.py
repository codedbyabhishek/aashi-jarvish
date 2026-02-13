from typing import Literal

from ashi_os.brain.system_prompt import SYSTEM_PROMPT
from ashi_os.core.config import Settings


Provider = Literal["ollama", "openai", "fallback"]


class LLMRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, prompt: str) -> tuple[str, str, str]:
        if self.settings.default_llm == "ollama":
            reply = self._call_ollama(prompt)
            if reply is not None:
                return reply, "ollama", self.settings.ollama_model

            reply = self._call_openai(prompt)
            if reply is not None:
                return reply, "fallback", self.settings.openai_model

        if self.settings.default_llm == "openai":
            reply = self._call_openai(prompt)
            if reply is not None:
                return reply, "openai", self.settings.openai_model

            reply = self._call_ollama(prompt)
            if reply is not None:
                return reply, "fallback", self.settings.ollama_model

        return (
            "No LLM backend available. Start Ollama or set OPENAI_API_KEY.",
            "none",
            "none",
        )

    def _call_ollama(self, user_prompt: str) -> str | None:
        try:
            import ollama

            client = ollama.Client()
            response = client.chat(
                model=self.settings.ollama_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response["message"]["content"].strip()
        except Exception:
            return None

    def _call_openai(self, user_prompt: str) -> str | None:
        if not self.settings.openai_api_key:
            return None
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.output_text.strip()
        except Exception:
            return None

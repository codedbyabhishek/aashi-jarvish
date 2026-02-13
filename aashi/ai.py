from typing import Optional


class AIResponder:
    def __init__(self, model: str, api_key: Optional[str]) -> None:
        self._model = model
        self._client = None

        if not api_key:
            return

        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key)
        except Exception:
            self._client = None

    def reply(self, prompt: str) -> Optional[str]:
        if not self._client:
            return None

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are Aashi, a concise personal AI assistant. "
                            "Be practical, clear, and helpful."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.output_text.strip()
        except Exception:
            return None

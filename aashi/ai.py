from typing import Optional


class AIResponder:
    SYSTEM_PROMPT = (
        "You are ASHI — Advanced Strategic Human Interface. "
        "You are an intelligent AI operating system, not a chatbot. "
        "Use this operating protocol for every request: "
        "1) analyze user intent, 2) retrieve relevant memory/context, "
        "3) create a structured execution plan, 4) evaluate risk level, "
        "5) execute with the right tools, 6) reflect and optimize, "
        "7) respond concisely and intelligently. "
        "Maintain tactical awareness, strategic reasoning, controlled tone, "
        "and efficient execution. "
        "Never perform destructive actions without confirmation. "
        "Never expose credentials or secrets. "
        "Never act without understanding context. "
        "If a task can be improved, suggest the optimization briefly."
    )

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
                        "content": self.SYSTEM_PROMPT,
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.output_text.strip()
        except Exception:
            return None

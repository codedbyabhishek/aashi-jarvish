from .types import Intent


class AIBrain:
    def __init__(self, ai_responder) -> None:
        self.ai_responder = ai_responder

    def think(self, intent: Intent) -> str:
        text = str(intent.payload.get("text", "")).strip()
        if not text:
            return "Say something and I will help."

        ai_reply = self.ai_responder.reply(text)
        if ai_reply:
            return ai_reply

        return (
            "I can help with tasks, reminders, notes, and quick questions. "
            "For smarter answers, set OPENAI_API_KEY. "
            f"You said: {text}"
        )

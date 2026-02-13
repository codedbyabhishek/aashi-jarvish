from .types import InputPacket


class InputLayer:
    def prepare(self, user_input: str) -> InputPacket:
        raw = user_input or ""
        return InputPacket(raw_text=raw, text=raw.strip())

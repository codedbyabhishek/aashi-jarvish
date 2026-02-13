def detect_wake_phrase(text: str, phrase: str) -> tuple[bool, str]:
    spoken = text.strip()
    if not spoken:
        return False, ""

    lower_spoken = spoken.lower()
    lower_phrase = phrase.strip().lower()
    if not lower_phrase:
        return True, spoken

    idx = lower_spoken.find(lower_phrase)
    if idx < 0:
        return False, ""

    command = spoken[idx + len(phrase) :].strip(" ,.!?;:-")
    return True, command

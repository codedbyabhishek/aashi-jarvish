from ashi_os.voice.wake_word import detect_wake_phrase


def test_detect_wake_phrase_extracts_command() -> None:
    ok, command = detect_wake_phrase("Hey Aashi open app safari", "hey aashi")
    assert ok is True
    assert command.lower() == "open app safari"


def test_detect_wake_phrase_missing() -> None:
    ok, command = detect_wake_phrase("open app safari", "hey aashi")
    assert ok is False
    assert command == ""

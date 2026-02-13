from aashi.assistant import AashiAssistant


def main() -> None:
    assistant = AashiAssistant()
    print(assistant.greet())

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nAashi: Goodbye.")
            break

        reply = assistant.handle(user_input)
        if reply == assistant.EXIT_SIGNAL:
            print("Aashi: Goodbye.")
            break

        print(f"Aashi: {reply}")
        assistant.speak(reply)


if __name__ == "__main__":
    main()

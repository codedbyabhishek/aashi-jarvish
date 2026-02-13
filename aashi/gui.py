import threading
import time
import tkinter as tk
from tkinter import ttk

from .assistant import AashiAssistant


class AashiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.assistant = AashiAssistant()
        self._build_window()
        self._build_layout()
        self._load_initial_data()
        self._post_bot_message("ASHI is ready.")

    def _build_window(self) -> None:
        self.root.title("ASHI")
        self.root.geometry("1280x820")
        self.root.minsize(980, 660)
        self.root.configure(bg="#0E1116")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#0E1116")
        style.configure("Panel.TFrame", background="#141923")
        style.configure("SubPanel.TFrame", background="#1A2130")
        style.configure(
            "Title.TLabel",
            background="#0E1116",
            foreground="#EAF0FB",
            font=("Avenir Next", 18, "bold"),
        )
        style.configure(
            "Label.TLabel",
            background="#141923",
            foreground="#C5D2E8",
            font=("Avenir Next", 10),
        )
        style.configure(
            "Section.TLabel",
            background="#141923",
            foreground="#F2F7FF",
            font=("Avenir Next", 11, "bold"),
        )

    def _build_layout(self) -> None:
        wrapper = ttk.Frame(self.root, style="App.TFrame", padding=14)
        wrapper.pack(fill="both", expand=True)
        wrapper.grid_columnconfigure(0, weight=30)
        wrapper.grid_columnconfigure(1, weight=70)
        wrapper.grid_rowconfigure(1, weight=1)

        top = ttk.Frame(wrapper, style="App.TFrame")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(top, text="ASHI", style="Title.TLabel").pack(side="left")
        self.status_text = tk.StringVar(value="Online")
        status = tk.Label(
            top,
            textvariable=self.status_text,
            bg="#0E1116",
            fg="#7BD88F",
            font=("Avenir Next", 10, "bold"),
        )
        status.pack(side="right")

        self.left = ttk.Frame(wrapper, style="Panel.TFrame", padding=12)
        self.left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        self.right = ttk.Frame(wrapper, style="Panel.TFrame", padding=12)
        self.right.grid(row=1, column=1, sticky="nsew", padx=(8, 0))

        self._build_controls()
        self._build_chat()

    def _build_controls(self) -> None:
        ttk.Label(self.left, text="Voice", style="Section.TLabel").pack(anchor="w")

        state_box = ttk.Frame(self.left, style="Panel.TFrame")
        state_box.pack(fill="x", pady=(6, 10))
        self.mode_label = ttk.Label(state_box, text="Mode: system", style="Label.TLabel")
        self.mode_label.pack(anchor="w")
        self.voice_label = ttk.Label(state_box, text="Voice: Samantha", style="Label.TLabel")
        self.voice_label.pack(anchor="w")

        mode_row = ttk.Frame(self.left, style="Panel.TFrame")
        mode_row.pack(fill="x", pady=(0, 8))
        ttk.Label(mode_row, text="Output mode", style="Label.TLabel").pack(side="left")
        self.mode_var = tk.StringVar(value=self.assistant.memory.voice_mode())
        combo = ttk.Combobox(
            mode_row,
            values=["system", "file", "clone"],
            state="readonly",
            width=10,
            textvariable=self.mode_var,
        )
        combo.pack(side="right")
        combo.bind("<<ComboboxSelected>>", lambda _e: self._submit_message(f"voice mode {self.mode_var.get()}"))

        ttk.Label(self.left, text="System voices", style="Label.TLabel").pack(anchor="w")
        self.voice_list = tk.Listbox(
            self.left,
            height=5,
            bg="#1A2130",
            fg="#E6EEFC",
            selectbackground="#2B3A57",
            borderwidth=0,
            highlightthickness=0,
            font=("Avenir Next", 10),
        )
        self.voice_list.pack(fill="x", pady=(4, 6))

        voice_btn = ttk.Frame(self.left, style="Panel.TFrame")
        voice_btn.pack(fill="x", pady=(0, 10))
        self._btn(voice_btn, "Refresh", self._load_voices).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._btn(voice_btn, "Use", self._set_selected_system_voice).pack(side="left", fill="x", expand=True, padx=(4, 0))

        ttk.Label(self.left, text="Voice files", style="Label.TLabel").pack(anchor="w")
        self.file_list = tk.Listbox(
            self.left,
            height=5,
            bg="#1A2130",
            fg="#E6EEFC",
            selectbackground="#2B3A57",
            borderwidth=0,
            highlightthickness=0,
            font=("Avenir Next", 10),
        )
        self.file_list.pack(fill="x", pady=(4, 6))

        file_btn = ttk.Frame(self.left, style="Panel.TFrame")
        file_btn.pack(fill="x", pady=(0, 8))
        self._btn(file_btn, "Refresh", self._load_voice_files).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._btn(file_btn, "Use", self._set_selected_voice_file).pack(side="left", fill="x", expand=True, padx=(4, 0))

        tools_btn = ttk.Frame(self.left, style="Panel.TFrame")
        tools_btn.pack(fill="x", pady=(0, 10))
        self._btn(tools_btn, "Voice input", self._run_voice_input_from_selected_file).pack(
            side="left", fill="x", expand=True, padx=(0, 4)
        )
        self._btn(tools_btn, "Train clone", self._train_clone_from_selected_file).pack(
            side="left", fill="x", expand=True, padx=(4, 0)
        )

        ttk.Separator(self.left).pack(fill="x", pady=10)

        ttk.Label(self.left, text="Quick actions", style="Section.TLabel").pack(anchor="w")
        quick = ttk.Frame(self.left, style="Panel.TFrame")
        quick.pack(fill="x", pady=(6, 0))
        commands = [
            ("Time", "time"),
            ("Date", "date"),
            ("Notes", "notes"),
            ("Help", "help"),
            ("Voice on", "voice on"),
            ("Voice off", "voice off"),
            ("Wake status", "wake status"),
            ("Setup status", "setup status"),
        ]
        for idx, (label, cmd) in enumerate(commands):
            btn = self._btn(quick, label, lambda c=cmd: self._submit_message(c))
            btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=4)
        quick.grid_columnconfigure(0, weight=1)
        quick.grid_columnconfigure(1, weight=1)

    def _build_chat(self) -> None:
        ttk.Label(self.right, text="Conversation", style="Section.TLabel").pack(anchor="w")

        chat_wrap = ttk.Frame(self.right, style="SubPanel.TFrame", padding=6)
        chat_wrap.pack(fill="both", expand=True, pady=(6, 10))

        self.chat = tk.Text(
            chat_wrap,
            bg="#1A2130",
            fg="#E7EEFB",
            insertbackground="#E7EEFB",
            relief="flat",
            borderwidth=0,
            wrap="word",
            font=("Avenir Next", 11),
            state="disabled",
        )
        self.chat.pack(fill="both", expand=True)
        self.chat.tag_configure("time", foreground="#8FA4C7")
        self.chat.tag_configure("you", foreground="#93C5FD")
        self.chat.tag_configure("ashi", foreground="#E7EEFB")

        input_row = ttk.Frame(self.right, style="Panel.TFrame")
        input_row.pack(fill="x")

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_row,
            textvariable=self.input_var,
            bg="#1A2130",
            fg="#E7EEFB",
            insertbackground="#E7EEFB",
            relief="flat",
            borderwidth=0,
            font=("Avenir Next", 12),
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda _e: self._submit_from_entry())

        self.send_btn = self._btn(input_row, "Send", self._submit_from_entry, bg="#2D3F61")
        self.send_btn.pack(side="right")

    def _btn(self, parent, text, command, bg="#23314D"):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="#EAF0FB",
            activebackground="#344A71",
            activeforeground="#FFFFFF",
            borderwidth=0,
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
            font=("Avenir Next", 10, "bold"),
        )

    def _load_initial_data(self) -> None:
        self._load_voices()
        self._load_voice_files()
        self._sync_status_labels()

    def _submit_from_entry(self) -> None:
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._submit_message(text)

    def _submit_message(self, message: str) -> None:
        self._post_user_message(message)
        self.send_btn.configure(state="disabled")
        self.input_entry.configure(state="disabled")
        self.status_text.set("Processing")
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()

    def _process_message(self, message: str) -> None:
        reply = self.assistant.handle(message)
        self.root.after(0, lambda: self._finish_response(reply))

    def _finish_response(self, reply: str) -> None:
        if reply == self.assistant.EXIT_SIGNAL:
            self._post_bot_message("Goodbye.")
            self._speak_async("Goodbye.")
            self.root.after(500, self.root.destroy)
            return

        self._post_bot_message(reply)
        self._sync_status_labels()
        self._speak_async(reply)
        self.send_btn.configure(state="normal")
        self.input_entry.configure(state="normal")
        self.input_entry.focus_set()
        self.status_text.set("Online")

    def _speak_async(self, text: str) -> None:
        threading.Thread(target=self.assistant.speak, args=(text,), daemon=True).start()

    def _append(self, speaker: str, text: str, tag: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self.chat.configure(state="normal")
        self.chat.insert("end", f"[{stamp}] ", "time")
        self.chat.insert("end", f"{speaker}: ", tag)
        self.chat.insert("end", f"{text}\n\n", tag)
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _post_user_message(self, text: str) -> None:
        self._append("You", text, "you")

    def _post_bot_message(self, text: str) -> None:
        self._append("ASHI", text, "ashi")

    def _load_voices(self) -> None:
        self.voice_list.delete(0, tk.END)
        for v in self.assistant.voice.available_system_voices(limit=80):
            self.voice_list.insert(tk.END, v)

    def _load_voice_files(self) -> None:
        self.file_list.delete(0, tk.END)
        for f in self.assistant.voice.available_voice_files(limit=80):
            self.file_list.insert(tk.END, f)

    def _set_selected_system_voice(self) -> None:
        cur = self.voice_list.curselection()
        if not cur:
            return
        self._submit_message(f"voice {self.voice_list.get(cur[0])}")

    def _set_selected_voice_file(self) -> None:
        cur = self.file_list.curselection()
        if not cur:
            return
        self._submit_message(f"voicefile {self.file_list.get(cur[0])}")

    def _train_clone_from_selected_file(self) -> None:
        cur = self.file_list.curselection()
        if not cur:
            self._post_bot_message("Select a voice file first.")
            return
        self._submit_message(f"clonevoice {self.file_list.get(cur[0])} ASHI Clone")

    def _run_voice_input_from_selected_file(self) -> None:
        cur = self.file_list.curselection()
        if not cur:
            self._post_bot_message("Select an audio file first.")
            return
        self._submit_message(f"listen {self.file_list.get(cur[0])}")

    def _sync_status_labels(self) -> None:
        mode = self.assistant.memory.voice_mode()
        self.mode_label.configure(text=f"Mode: {mode}")
        if mode == "file":
            label = self.assistant.memory.voice_file() or "(not set)"
        elif mode == "clone":
            label = self.assistant.memory.clone_voice_name() or "(not set)"
        else:
            label = self.assistant.memory.voice_name()
        self.voice_label.configure(text=f"Voice: {label}")
        self.mode_var.set(mode)


def run_gui() -> None:
    root = tk.Tk()
    app = AashiApp(root)
    app.input_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    run_gui()

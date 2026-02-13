import threading
import tkinter as tk
from tkinter import ttk

from .assistant import AashiAssistant


class AashiDesktopApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.assistant = AashiAssistant()
        self._build_window()
        self._build_layout()
        self._load_initial_data()
        self._post_bot_message(self.assistant.greet())

    def _build_window(self) -> None:
        self.root.title("Aashi | Personal Jarvish")
        self.root.geometry("1180x760")
        self.root.minsize(980, 640)
        self.root.configure(bg="#0B1220")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Card.TFrame", background="#121C2E")
        self.style.configure("SidebarCard.TFrame", background="#10182A")
        self.style.configure(
            "Title.TLabel",
            background="#0B1220",
            foreground="#EAF1FF",
            font=("Avenir Next", 22, "bold"),
        )
        self.style.configure(
            "Subtle.TLabel",
            background="#0B1220",
            foreground="#9FB1CC",
            font=("Avenir Next", 10),
        )
        self.style.configure(
            "CardLabel.TLabel",
            background="#121C2E",
            foreground="#DDE8FF",
            font=("Avenir Next", 10),
        )

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)

        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=5)
        container.grid_rowconfigure(0, weight=1)

        self.sidebar = ttk.Frame(container, style="SidebarCard.TFrame", padding=16)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.chat_panel = ttk.Frame(container, style="Card.TFrame", padding=16)
        self.chat_panel.grid(row=0, column=1, sticky="nsew")

        self._build_sidebar()
        self._build_chat_panel()

    def _build_sidebar(self) -> None:
        header = ttk.Label(self.sidebar, text="AASHI", style="Title.TLabel")
        header.configure(background="#10182A")
        header.pack(anchor="w")

        subtitle = ttk.Label(
            self.sidebar,
            text="Your personal Jarvish control center",
            style="Subtle.TLabel",
        )
        subtitle.configure(background="#10182A")
        subtitle.pack(anchor="w", pady=(0, 14))

        status_frame = ttk.Frame(self.sidebar, style="SidebarCard.TFrame")
        status_frame.pack(fill="x", pady=(0, 12))

        self.mode_label = ttk.Label(status_frame, text="Mode: system", style="CardLabel.TLabel")
        self.mode_label.configure(background="#10182A")
        self.mode_label.pack(anchor="w")

        self.voice_label = ttk.Label(status_frame, text="Voice: Samantha", style="CardLabel.TLabel")
        self.voice_label.configure(background="#10182A")
        self.voice_label.pack(anchor="w", pady=(4, 0))

        quick_title = ttk.Label(self.sidebar, text="Quick Actions", style="CardLabel.TLabel")
        quick_title.configure(background="#10182A")
        quick_title.pack(anchor="w", pady=(6, 6))

        quick_actions = [
            ("Time", "time"),
            ("Date", "date"),
            ("Help", "help"),
            ("Notes", "notes"),
            ("Voice On", "voice on"),
            ("Voice Off", "voice off"),
        ]
        grid = ttk.Frame(self.sidebar, style="SidebarCard.TFrame")
        grid.pack(fill="x")

        for idx, (label, cmd) in enumerate(quick_actions):
            btn = tk.Button(
                grid,
                text=label,
                command=lambda c=cmd: self._submit_message(c),
                bg="#1B2A45",
                fg="#E8F0FF",
                activebackground="#223556",
                activeforeground="#FFFFFF",
                borderwidth=0,
                font=("Avenir Next", 10, "bold"),
                padx=12,
                pady=8,
                cursor="hand2",
            )
            btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=4)

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        separator = ttk.Separator(self.sidebar)
        separator.pack(fill="x", pady=14)

        voice_title = ttk.Label(self.sidebar, text="Voice Settings", style="CardLabel.TLabel")
        voice_title.configure(background="#10182A")
        voice_title.pack(anchor="w")

        mode_row = ttk.Frame(self.sidebar, style="SidebarCard.TFrame")
        mode_row.pack(fill="x", pady=(8, 6))
        ttk.Label(mode_row, text="Mode", style="CardLabel.TLabel").pack(side="left")

        self.mode_var = tk.StringVar(value=self.assistant.memory.voice_mode())
        mode_combo = ttk.Combobox(
            mode_row,
            values=["system", "file"],
            textvariable=self.mode_var,
            state="readonly",
            width=10,
        )
        mode_combo.pack(side="right")
        mode_combo.bind("<<ComboboxSelected>>", lambda _e: self._submit_message(f"voice mode {self.mode_var.get()}"))

        voices_lbl = ttk.Label(self.sidebar, text="System Voices", style="CardLabel.TLabel")
        voices_lbl.configure(background="#10182A")
        voices_lbl.pack(anchor="w", pady=(4, 2))

        self.voice_list = tk.Listbox(
            self.sidebar,
            height=5,
            bg="#13213A",
            fg="#E8F0FF",
            selectbackground="#2D4874",
            borderwidth=0,
            highlightthickness=0,
            font=("Avenir Next", 10),
        )
        self.voice_list.pack(fill="x")

        voice_btn_row = ttk.Frame(self.sidebar, style="SidebarCard.TFrame")
        voice_btn_row.pack(fill="x", pady=(5, 10))

        tk.Button(
            voice_btn_row,
            text="Refresh",
            command=self._load_voices,
            bg="#23385D",
            fg="#E8F0FF",
            borderwidth=0,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            voice_btn_row,
            text="Use Selected",
            command=self._set_selected_system_voice,
            bg="#3A6AE0",
            fg="#FFFFFF",
            borderwidth=0,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side="right")

        files_lbl = ttk.Label(self.sidebar, text="Voice Files (./save)", style="CardLabel.TLabel")
        files_lbl.configure(background="#10182A")
        files_lbl.pack(anchor="w", pady=(2, 2))

        self.file_list = tk.Listbox(
            self.sidebar,
            height=4,
            bg="#13213A",
            fg="#E8F0FF",
            selectbackground="#2D4874",
            borderwidth=0,
            highlightthickness=0,
            font=("Avenir Next", 10),
        )
        self.file_list.pack(fill="x")

        file_btn_row = ttk.Frame(self.sidebar, style="SidebarCard.TFrame")
        file_btn_row.pack(fill="x", pady=(5, 0))

        tk.Button(
            file_btn_row,
            text="Refresh",
            command=self._load_voice_files,
            bg="#23385D",
            fg="#E8F0FF",
            borderwidth=0,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            file_btn_row,
            text="Use File",
            command=self._set_selected_voice_file,
            bg="#3A6AE0",
            fg="#FFFFFF",
            borderwidth=0,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side="right")

    def _build_chat_panel(self) -> None:
        top = ttk.Frame(self.chat_panel, style="Card.TFrame")
        top.pack(fill="x")

        title = ttk.Label(top, text="Conversation", style="Title.TLabel")
        title.configure(background="#121C2E", font=("Avenir Next", 18, "bold"))
        title.pack(anchor="w")

        note = ttk.Label(top, text="Talk naturally or use commands", style="Subtle.TLabel")
        note.configure(background="#121C2E")
        note.pack(anchor="w", pady=(0, 8))

        chat_wrap = tk.Frame(self.chat_panel, bg="#121C2E")
        chat_wrap.pack(fill="both", expand=True, pady=(4, 10))

        self.chat_canvas = tk.Canvas(
            chat_wrap,
            bg="#121C2E",
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(chat_wrap, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)

        self.messages_frame = tk.Frame(self.chat_canvas, bg="#121C2E")
        self.messages_window = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        self.messages_frame.bind("<Configure>", self._on_messages_configure)
        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)

        input_row = tk.Frame(self.chat_panel, bg="#121C2E")
        input_row.pack(fill="x")

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_row,
            textvariable=self.input_var,
            bg="#0E1729",
            fg="#F1F6FF",
            insertbackground="#F1F6FF",
            borderwidth=0,
            font=("Avenir Next", 12),
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda _e: self._submit_from_entry())

        self.send_button = tk.Button(
            input_row,
            text="Send",
            command=self._submit_from_entry,
            bg="#3A6AE0",
            fg="#FFFFFF",
            activebackground="#4B79E7",
            activeforeground="#FFFFFF",
            borderwidth=0,
            font=("Avenir Next", 11, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
        )
        self.send_button.pack(side="right")

    def _load_initial_data(self) -> None:
        self._load_voices()
        self._load_voice_files()
        self._sync_status_labels()

    def _on_messages_configure(self, _event: tk.Event) -> None:
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.chat_canvas.itemconfigure(self.messages_window, width=event.width)

    def _submit_from_entry(self) -> None:
        message = self.input_var.get().strip()
        if not message:
            return
        self.input_var.set("")
        self._submit_message(message)

    def _submit_message(self, message: str) -> None:
        self._post_user_message(message)
        self.send_button.configure(state="disabled")
        self.input_entry.configure(state="disabled")

        worker = threading.Thread(target=self._process_message, args=(message,), daemon=True)
        worker.start()

    def _process_message(self, message: str) -> None:
        reply = self.assistant.handle(message)
        self.root.after(0, lambda: self._finish_response(reply))

    def _finish_response(self, reply: str) -> None:
        if reply == self.assistant.EXIT_SIGNAL:
            bye = "Goodbye."
            self._post_bot_message(bye)
            self._speak_async(bye)
            self.root.after(650, self.root.destroy)
            return

        self._post_bot_message(reply)
        self._sync_status_labels()
        self._speak_async(reply)

        self.send_button.configure(state="normal")
        self.input_entry.configure(state="normal")
        self.input_entry.focus_set()

    def _speak_async(self, text: str) -> None:
        threading.Thread(target=self.assistant.speak, args=(text,), daemon=True).start()

    def _post_user_message(self, text: str) -> None:
        self._add_message("You", text, user=True)

    def _post_bot_message(self, text: str) -> None:
        self._add_message("Aashi", text, user=False)

    def _add_message(self, speaker: str, text: str, user: bool) -> None:
        outer = tk.Frame(self.messages_frame, bg="#121C2E")
        outer.pack(fill="x", pady=6, padx=8)

        bubble_bg = "#3A6AE0" if user else "#1D2C45"
        bubble = tk.Frame(outer, bg=bubble_bg, padx=12, pady=10)

        if user:
            bubble.pack(anchor="e", padx=(120, 0))
        else:
            bubble.pack(anchor="w", padx=(0, 120))

        who = tk.Label(
            bubble,
            text=speaker,
            bg=bubble_bg,
            fg="#D9E6FF",
            font=("Avenir Next", 9, "bold"),
            anchor="w",
        )
        who.pack(anchor="w")

        msg = tk.Label(
            bubble,
            text=text,
            bg=bubble_bg,
            fg="#FFFFFF",
            justify="left",
            wraplength=560,
            font=("Avenir Next", 11),
        )
        msg.pack(anchor="w", pady=(3, 0))

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _load_voices(self) -> None:
        self.voice_list.delete(0, tk.END)
        voices = self.assistant.voice.available_system_voices(limit=80)
        for voice in voices:
            self.voice_list.insert(tk.END, voice)

    def _load_voice_files(self) -> None:
        self.file_list.delete(0, tk.END)
        files = self.assistant.voice.available_voice_files(limit=80)
        for name in files:
            self.file_list.insert(tk.END, name)

    def _set_selected_system_voice(self) -> None:
        selection = self.voice_list.curselection()
        if not selection:
            return
        voice_name = self.voice_list.get(selection[0])
        self._submit_message(f"voice {voice_name}")

    def _set_selected_voice_file(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            return
        filename = self.file_list.get(selection[0])
        self._submit_message(f"voicefile {filename}")

    def _sync_status_labels(self) -> None:
        mode = self.assistant.memory.voice_mode()
        self.mode_label.configure(text=f"Mode: {mode}")

        if mode == "file":
            voice_name = self.assistant.memory.voice_file() or "(not set)"
        else:
            voice_name = self.assistant.memory.voice_name()
        self.voice_label.configure(text=f"Voice: {voice_name}")

        self.mode_var.set(mode)


def run_gui() -> None:
    root = tk.Tk()
    app = AashiDesktopApp(root)
    app.input_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    run_gui()

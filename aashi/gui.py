import math
import threading
import time
import tkinter as tk
from collections import deque

from .assistant import AashiAssistant


BG = "#03070F"
PANEL = "#081227"
PANEL_ALT = "#0B1734"
PANEL_SOFT = "#11254A"
BORDER = "#1E4477"
TEXT = "#EAF4FF"
TEXT_SOFT = "#97B8E4"
ACCENT_SOFT = "#93DDFF"
SUCCESS_BG = "#0F3B28"
SUCCESS_FG = "#8CF5BE"
WARN_BG = "#3D2A0E"
WARN_FG = "#FFD37A"


class AashiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.assistant = AashiAssistant()

        self._pulse = 0
        self._metrics_tick = 0
        self._wave_tick = 0
        self._history: list[str] = []
        self._history_index = 0
        self._events = deque(maxlen=18)

        self._build_window()
        self._build_layout()
        self._bind_shortcuts()
        self._load_initial_data()

        self._animate_hud()
        self._post_bot_message("ASHI is active. Awaiting your directive.")
        self._log_event("System initialized")

    def _build_window(self) -> None:
        self.root.title("ASHI Command Center")
        self.root.geometry("1520x930")
        self.root.minsize(1220, 760)
        self.root.configure(bg=BG)

    def _build_layout(self) -> None:
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True, padx=14, pady=12)

        self._build_header(shell)

        grid = tk.Frame(shell, bg=BG)
        grid.pack(fill="both", expand=True, pady=(12, 0))
        grid.grid_columnconfigure(0, weight=26)
        grid.grid_columnconfigure(1, weight=34)
        grid.grid_columnconfigure(2, weight=40)
        grid.grid_rowconfigure(0, weight=1)

        self.left = self._card(grid)
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.center = self._card(grid, alt=True)
        self.center.grid(row=0, column=1, sticky="nsew", padx=8)

        self.right = self._card(grid)
        self.right.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

    def _build_header(self, parent: tk.Frame) -> None:
        top = self._card(parent, alt=True)
        top.pack(fill="x")

        left = tk.Frame(top, bg=top["bg"])
        left.pack(side="left", padx=16, pady=12)
        tk.Label(left, text="ASHI", bg=top["bg"], fg=TEXT, font=("Avenir Next", 28, "bold")).pack(anchor="w")
        tk.Label(
            left,
            text="Advanced Strategic Human Interface",
            bg=top["bg"],
            fg=TEXT_SOFT,
            font=("Avenir Next", 10),
        ).pack(anchor="w")

        middle = tk.Frame(top, bg=top["bg"])
        middle.pack(side="left", padx=20)
        tk.Label(middle, text="TACTICAL STATUS", bg=top["bg"], fg=ACCENT_SOFT, font=("Avenir Next", 9, "bold")).pack(anchor="w")
        self.top_hint = tk.Label(middle, text="Voice + command systems ready", bg=top["bg"], fg=TEXT_SOFT, font=("Avenir Next", 10))
        self.top_hint.pack(anchor="w")

        right = tk.Frame(top, bg=top["bg"])
        right.pack(side="right", padx=16, pady=12)

        self.status_text = tk.StringVar(value="ONLINE")
        self.status_chip = tk.Label(
            right,
            textvariable=self.status_text,
            bg=SUCCESS_BG,
            fg=SUCCESS_FG,
            font=("Avenir Next", 10, "bold"),
            padx=14,
            pady=6,
            borderwidth=0,
        )
        self.status_chip.pack(anchor="e")

    def _build_left_panel(self) -> None:
        wrap = tk.Frame(self.left, bg=self.left["bg"])
        wrap.pack(fill="both", expand=True, padx=12, pady=12)

        self._section(wrap, "Voice Matrix")

        identity = tk.Frame(wrap, bg=PANEL_SOFT, highlightthickness=1, highlightbackground=BORDER)
        identity.pack(fill="x", pady=(8, 10))
        self.mode_label = tk.Label(identity, text="Mode: system", bg=PANEL_SOFT, fg=TEXT, font=("Avenir Next", 10, "bold"))
        self.mode_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.voice_label = tk.Label(identity, text="Voice: Samantha", bg=PANEL_SOFT, fg=TEXT_SOFT, font=("Avenir Next", 10))
        self.voice_label.pack(anchor="w", padx=10, pady=(0, 10))

        self._sub(wrap, "Output mode")
        self.mode_var = tk.StringVar(value=self.assistant.memory.voice_mode())
        mode_menu = tk.OptionMenu(wrap, self.mode_var, "system", "file", "clone", command=lambda v: self._submit_message(f"voice mode {v}"))
        mode_menu.configure(bg="#142A53", fg=TEXT, activebackground="#1A3767", activeforeground=TEXT, relief="flat", borderwidth=0)
        mode_menu["menu"].configure(bg="#142A53", fg=TEXT, activebackground="#1A3767", activeforeground=TEXT, borderwidth=0)
        mode_menu.pack(fill="x", pady=(4, 10))

        self._sub(wrap, "System voices")
        self.voice_list = self._listbox(wrap, 5)
        self.voice_list.pack(fill="x", pady=(4, 6))

        row1 = tk.Frame(wrap, bg=wrap["bg"])
        row1.pack(fill="x", pady=(0, 10))
        self._btn(row1, "Refresh", self._load_voices).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._btn(row1, "Apply", self._set_selected_system_voice, accent=True).pack(side="left", fill="x", expand=True, padx=(4, 0))

        self._sub(wrap, "Voice samples")
        self.file_list = self._listbox(wrap, 5)
        self.file_list.pack(fill="x", pady=(4, 6))

        row2 = tk.Frame(wrap, bg=wrap["bg"])
        row2.pack(fill="x", pady=(0, 10))
        self._btn(row2, "Refresh", self._load_voice_files).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._btn(row2, "Use file", self._set_selected_voice_file, accent=True).pack(side="left", fill="x", expand=True, padx=(4, 0))

        row3 = tk.Frame(wrap, bg=wrap["bg"])
        row3.pack(fill="x", pady=(0, 12))
        self._btn(row3, "Voice input", self._run_voice_input_from_selected_file).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._btn(row3, "Train clone", self._train_clone_from_selected_file).pack(side="left", fill="x", expand=True, padx=(4, 0))

        self._section(wrap, "Quick Actions")
        quick = tk.Frame(wrap, bg=wrap["bg"])
        quick.pack(fill="x", pady=(8, 0))

        commands = [
            ("Time", "time"),
            ("Date", "date"),
            ("Notes", "notes"),
            ("Help", "help"),
            ("Voice On", "voice on"),
            ("Voice Off", "voice off"),
            ("Wake", "wake status"),
            ("Setup", "setup status"),
        ]
        for index, (label, cmd) in enumerate(commands):
            button = self._btn(quick, label, lambda c=cmd: self._submit_message(c))
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=4, pady=4)
        quick.grid_columnconfigure(0, weight=1)
        quick.grid_columnconfigure(1, weight=1)

    def _build_center_panel(self) -> None:
        wrap = tk.Frame(self.center, bg=self.center["bg"])
        wrap.pack(fill="both", expand=True, padx=12, pady=12)

        self._section(wrap, "AI Core")

        core_card = tk.Frame(wrap, bg="#081935", highlightthickness=1, highlightbackground=BORDER)
        core_card.pack(fill="x", pady=(8, 10))

        self.core = tk.Canvas(core_card, bg="#081935", height=290, highlightthickness=0, borderwidth=0)
        self.core.pack(fill="x", padx=8, pady=(8, 4))
        self.core.bind("<Configure>", lambda _e: self._draw_core())

        self.wave = tk.Canvas(core_card, bg="#081935", height=62, highlightthickness=0, borderwidth=0)
        self.wave.pack(fill="x", padx=8, pady=(0, 8))
        self.wave.bind("<Configure>", lambda _e: self._draw_waveform())

        meter_grid = tk.Frame(wrap, bg=wrap["bg"])
        meter_grid.pack(fill="x", pady=(0, 10))
        self.m_cpu = self._meter(meter_grid, "CPU", "36%")
        self.m_mem = self._meter(meter_grid, "MEM", "44%")
        self.m_net = self._meter(meter_grid, "NET", "LOW")
        self.m_cpu.grid(row=0, column=0, padx=4, sticky="ew")
        self.m_mem.grid(row=0, column=1, padx=4, sticky="ew")
        self.m_net.grid(row=0, column=2, padx=4, sticky="ew")
        meter_grid.grid_columnconfigure(0, weight=1)
        meter_grid.grid_columnconfigure(1, weight=1)
        meter_grid.grid_columnconfigure(2, weight=1)

        events = tk.Frame(wrap, bg=PANEL_SOFT, highlightthickness=1, highlightbackground=BORDER)
        events.pack(fill="both", expand=True)

        bar = tk.Frame(events, bg=PANEL_SOFT)
        bar.pack(fill="x", padx=10, pady=(10, 6))
        tk.Label(bar, text="Activity Rail", bg=PANEL_SOFT, fg=TEXT, font=("Avenir Next", 11, "bold")).pack(side="left")
        self._btn(bar, "Clear", self._clear_events).pack(side="right")

        self.event_list = tk.Listbox(
            events,
            height=8,
            bg="#102546",
            fg="#DCEBFF",
            selectbackground="#245EAD",
            selectforeground="#FFFFFF",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#2B5A8E",
            highlightcolor="#2B5A8E",
            font=("JetBrains Mono", 10),
        )
        self.event_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_right_panel(self) -> None:
        wrap = tk.Frame(self.right, bg=self.right["bg"])
        wrap.pack(fill="both", expand=True, padx=12, pady=12)

        self._section(wrap, "Command Console")
        self._sub(wrap, "Ctrl+Enter send  |  Ctrl+L clear chat  |  Up/Down history")

        preset_row = tk.Frame(wrap, bg=wrap["bg"])
        preset_row.pack(fill="x", pady=(8, 8))
        presets = [
            ("System Check", "setup status"),
            ("Wake Ready", "wake status"),
            ("List Notes", "notes"),
            ("Voice Files", "voicefiles"),
        ]
        for index, (label, command) in enumerate(presets):
            self._btn(preset_row, label, lambda c=command: self._submit_message(c)).grid(
                row=0,
                column=index,
                sticky="ew",
                padx=3,
            )
            preset_row.grid_columnconfigure(index, weight=1)

        chat_card = tk.Frame(wrap, bg="#071427", highlightthickness=1, highlightbackground=BORDER)
        chat_card.pack(fill="both", expand=True, pady=(0, 10))

        self.chat = tk.Text(
            chat_card,
            bg="#071427",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            wrap="word",
            font=("JetBrains Mono", 11),
            state="disabled",
            padx=14,
            pady=12,
        )
        self.chat.pack(fill="both", expand=True)
        self.chat.tag_configure("time", foreground="#6486BB")
        self.chat.tag_configure("you", foreground="#7FD2FF")
        self.chat.tag_configure("ashi", foreground="#EAF4FF")

        input_row = tk.Frame(wrap, bg=wrap["bg"])
        input_row.pack(fill="x")

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_row,
            textvariable=self.input_var,
            bg="#10213F",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("JetBrains Mono", 12),
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda _e: self._submit_from_entry())
        self.input_entry.bind("<Up>", self._history_prev)
        self.input_entry.bind("<Down>", self._history_next)

        self.send_btn = self._btn(input_row, "Execute", self._submit_from_entry, accent=True)
        self.send_btn.pack(side="right")

    def _bind_shortcuts(self) -> None:
        self.root.bind_all("<Control-Return>", lambda _e: self._submit_from_entry())
        self.root.bind_all("<Control-l>", lambda _e: self._clear_chat())
        self.root.bind_all("<Escape>", lambda _e: self.input_entry.focus_set())

    def _card(self, parent, alt: bool = False):
        background = PANEL_ALT if alt else PANEL
        return tk.Frame(parent, bg=background, highlightthickness=1, highlightbackground=BORDER)

    def _section(self, parent, text: str) -> None:
        tk.Label(parent, text=text, bg=parent["bg"], fg=TEXT, font=("Avenir Next", 13, "bold")).pack(anchor="w")

    def _sub(self, parent, text: str) -> None:
        tk.Label(parent, text=text, bg=parent["bg"], fg=TEXT_SOFT, font=("Avenir Next", 10)).pack(anchor="w")

    def _listbox(self, parent: tk.Frame, height: int) -> tk.Listbox:
        return tk.Listbox(
            parent,
            height=height,
            bg="#0D1B36",
            fg="#DBE8FF",
            selectbackground="#245EAD",
            selectforeground="#FFFFFF",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#234473",
            highlightcolor="#234473",
            font=("Avenir Next", 10),
        )

    def _btn(self, parent, text, command, accent: bool = False):
        bg = "#16335D"
        active = "#1B4178"
        if accent:
            bg = "#2072D6"
            active = "#2B86F5"
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="#F4F9FF",
            activebackground=active,
            activeforeground="#FFFFFF",
            relief="flat",
            borderwidth=0,
            padx=11,
            pady=9,
            cursor="hand2",
            font=("Avenir Next", 10, "bold"),
        )

    def _meter(self, parent, title: str, value: str) -> tk.Frame:
        box = tk.Frame(parent, bg="#11284D", highlightthickness=1, highlightbackground="#245084")
        tk.Label(box, text=title, bg="#11284D", fg=TEXT_SOFT, font=("Avenir Next", 9, "bold")).pack(anchor="w", padx=8, pady=(7, 0))
        value_label = tk.Label(box, text=value, bg="#11284D", fg=ACCENT_SOFT, font=("Avenir Next", 10, "bold"))
        value_label.pack(anchor="w", padx=8, pady=(0, 7))
        box.value_label = value_label
        return box

    def _draw_core(self) -> None:
        canvas = self.core
        canvas.delete("all")

        width = max(canvas.winfo_width(), 340)
        height = max(canvas.winfo_height(), 250)
        cx, cy = width // 2, height // 2
        phase = self._pulse / 9.0

        glow = int(11 * (1 + math.sin(phase)))
        canvas.create_oval(cx - 142 - glow, cy - 118 - glow, cx + 142 + glow, cy + 118 + glow, outline="#123A68", width=1)
        canvas.create_oval(cx - 118, cy - 96, cx + 118, cy + 96, outline="#1D568D", width=2)
        canvas.create_oval(cx - 92, cy - 72, cx + 92, cy + 72, outline="#2A78C7", width=2)
        canvas.create_oval(cx - 55, cy - 40, cx + 55, cy + 40, fill="#1A84E1", outline="#7CD9FF", width=2)

        canvas.create_text(cx, cy - 2, text="ASHI", fill="#F0F8FF", font=("Avenir Next", 16, "bold"))
        canvas.create_text(cx, cy + 20, text="CORE ONLINE", fill="#A6D8FF", font=("Avenir Next", 9, "bold"))

        lines = [
            (22, 30, cx - 130, cy - 32),
            (width - 22, 30, cx + 130, cy - 32),
            (24, height - 26, cx - 130, cy + 32),
            (width - 24, height - 26, cx + 130, cy + 32),
        ]
        for x1, y1, x2, y2 in lines:
            canvas.create_line(x1, y1, x2, y2, fill="#2C7BC9", width=1)
            canvas.create_oval(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="#5AC7FF", outline="")

    def _draw_waveform(self) -> None:
        canvas = self.wave
        canvas.delete("all")

        width = max(canvas.winfo_width(), 240)
        height = max(canvas.winfo_height(), 48)
        mid = height // 2

        bars = 34
        step = width / bars
        active = self.status_text.get() == "WORKING"
        amp_base = 11 if active else 5

        for i in range(bars):
            phase = (self._wave_tick / 4.0) + (i * 0.45)
            amp = amp_base + int(8 * (1 + math.sin(phase)))
            x = int(i * step + step / 2)
            color = "#5ECFFF" if active else "#2A5A8E"
            canvas.create_line(x, mid - amp, x, mid + amp, fill=color, width=2)

        canvas.create_line(0, mid, width, mid, fill="#1C3F67", width=1)

    def _animate_hud(self) -> None:
        self._pulse = (self._pulse + 1) % 360
        self._metrics_tick += 1
        self._wave_tick += 1

        self._draw_core()
        self._draw_waveform()

        if self._metrics_tick % 9 == 0:
            cpu = 31 + int(9 * (1 + math.sin(self._pulse / 13.0)))
            mem = 40 + int(11 * (1 + math.cos(self._pulse / 14.0)))
            net = "LOW" if (self._pulse // 24) % 2 == 0 else "MID"
            self.m_cpu.value_label.configure(text=f"{cpu}%")
            self.m_mem.value_label.configure(text=f"{mem}%")
            self.m_net.value_label.configure(text=net)

        self.root.after(170, self._animate_hud)

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
        self._history.append(message)
        self._history_index = len(self._history)

        self._post_user_message(message)
        self._log_event(f"Command queued: {message}")

        self.send_btn.configure(state="disabled")
        self.input_entry.configure(state="disabled")
        self.status_text.set("WORKING")
        self.status_chip.configure(bg=WARN_BG, fg=WARN_FG)
        self.top_hint.configure(text="Executing command pipeline...")

        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()

    def _process_message(self, message: str) -> None:
        reply = self.assistant.handle(message)
        self.root.after(0, lambda: self._finish_response(reply))

    def _finish_response(self, reply: str) -> None:
        if reply == self.assistant.EXIT_SIGNAL:
            self._post_bot_message("Session closed. Goodbye.")
            self._speak_async("Goodbye.")
            self._log_event("Session terminated")
            self.root.after(400, self.root.destroy)
            return

        self._post_bot_message(reply)
        self._sync_status_labels()
        self._speak_async(reply)
        self._log_event("Command completed")

        self.send_btn.configure(state="normal")
        self.input_entry.configure(state="normal")
        self.input_entry.focus_set()
        self.status_text.set("ONLINE")
        self.status_chip.configure(bg=SUCCESS_BG, fg=SUCCESS_FG)
        self.top_hint.configure(text="Voice + command systems ready")

    def _append(self, speaker: str, text: str, tag: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self.chat.configure(state="normal")
        self.chat.insert("end", f"[{stamp}] ", "time")
        self.chat.insert("end", f"{speaker}: ", tag)
        self.chat.insert("end", f"{text}\n\n", tag)
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _post_user_message(self, text: str) -> None:
        self._append("YOU", text, "you")

    def _post_bot_message(self, text: str) -> None:
        self._append("ASHI", text, "ashi")

    def _log_event(self, message: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        line = f"[{stamp}] {message}"
        self._events.appendleft(line)

        self.event_list.delete(0, tk.END)
        for event in self._events:
            self.event_list.insert(tk.END, event)

    def _clear_events(self) -> None:
        self._events.clear()
        self.event_list.delete(0, tk.END)
        self._log_event("Activity rail cleared")

    def _clear_chat(self) -> None:
        self.chat.configure(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state="disabled")
        self._post_bot_message("Console cleared. Ready for next command.")
        self._log_event("Console cleared")

    def _history_prev(self, _event=None):
        if not self._history:
            return "break"
        self._history_index = max(0, self._history_index - 1)
        self.input_var.set(self._history[self._history_index])
        self.input_entry.icursor(tk.END)
        return "break"

    def _history_next(self, _event=None):
        if not self._history:
            return "break"
        self._history_index = min(len(self._history), self._history_index + 1)
        if self._history_index >= len(self._history):
            self.input_var.set("")
        else:
            self.input_var.set(self._history[self._history_index])
        self.input_entry.icursor(tk.END)
        return "break"

    def _speak_async(self, text: str) -> None:
        threading.Thread(target=self.assistant.speak, args=(text,), daemon=True).start()

    def _load_voices(self) -> None:
        self.voice_list.delete(0, tk.END)
        for voice in self.assistant.voice.available_system_voices(limit=80):
            self.voice_list.insert(tk.END, voice)

    def _load_voice_files(self) -> None:
        self.file_list.delete(0, tk.END)
        for file_name in self.assistant.voice.available_voice_files(limit=80):
            self.file_list.insert(tk.END, file_name)

    def _set_selected_system_voice(self) -> None:
        selection = self.voice_list.curselection()
        if not selection:
            self._post_bot_message("Select a system voice first.")
            self._log_event("Voice apply skipped: no system voice selected")
            return
        self._submit_message(f"voice {self.voice_list.get(selection[0])}")

    def _set_selected_voice_file(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            self._post_bot_message("Select a voice file first.")
            self._log_event("Voice file apply skipped: no file selected")
            return
        self._submit_message(f"voicefile {self.file_list.get(selection[0])}")

    def _train_clone_from_selected_file(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            self._post_bot_message("Select a voice file first.")
            self._log_event("Clone training skipped: no file selected")
            return
        self._submit_message(f"clonevoice {self.file_list.get(selection[0])} ASHI Clone")

    def _run_voice_input_from_selected_file(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            self._post_bot_message("Select an audio file first.")
            self._log_event("Voice input skipped: no file selected")
            return
        self._submit_message(f"listen {self.file_list.get(selection[0])}")

    def _sync_status_labels(self) -> None:
        mode = self.assistant.memory.voice_mode()
        self.mode_label.configure(text=f"Mode: {mode}")

        if mode == "file":
            voice_label = self.assistant.memory.voice_file() or "(not set)"
        elif mode == "clone":
            voice_label = self.assistant.memory.clone_voice_name() or "(not set)"
        else:
            voice_label = self.assistant.memory.voice_name()

        self.voice_label.configure(text=f"Voice: {voice_label}")
        self.mode_var.set(mode)


def run_gui() -> None:
    root = tk.Tk()
    app = AashiApp(root)
    app.input_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    run_gui()

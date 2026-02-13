import random
import threading
import time
import tkinter as tk
from tkinter import ttk

from .assistant import AashiAssistant


class AashiDashboardApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.assistant = AashiAssistant()
        self._psutil = self._load_psutil()
        self._net_last_bytes = None
        self._net_last_time = None
        self._sim_cpu = 42.0
        self._sim_mem = 51.0
        self._sim_net = 34.0
        self._particles = []
        self._build_window()
        self._build_layout()
        self._load_initial_data()
        self._post_bot_message(self.assistant.greet())
        self._animate_hud()

    def _load_psutil(self):
        try:
            import psutil  # type: ignore

            return psutil
        except Exception:
            return None

    def _build_window(self) -> None:
        self.root.title("ASHI // Advanced Strategic Human Interface")
        self.root.geometry("1600x940")
        self.root.minsize(1200, 760)
        self.root.configure(bg="#02060F")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Hud.TFrame", background="#02060F")
        self.style.configure("Panel.TFrame", background="#081224")
        self.style.configure("InnerPanel.TFrame", background="#0B1830")
        self.style.configure(
            "HudTitle.TLabel",
            background="#02060F",
            foreground="#7EE7FF",
            font=("Avenir Next", 21, "bold"),
        )
        self.style.configure(
            "PanelTitle.TLabel",
            background="#081224",
            foreground="#8DEBFF",
            font=("Avenir Next", 11, "bold"),
        )
        self.style.configure(
            "PanelText.TLabel",
            background="#081224",
            foreground="#BBD6F2",
            font=("Avenir Next", 10),
        )

        self.style.configure(
            "Hud.Horizontal.TProgressbar",
            troughcolor="#0B1830",
            background="#44D9FF",
            bordercolor="#0B1830",
            lightcolor="#72ECFF",
            darkcolor="#24BBD8",
        )

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, style="Hud.TFrame", padding=14)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=27)
        container.grid_columnconfigure(1, weight=46)
        container.grid_columnconfigure(2, weight=27)
        container.grid_rowconfigure(1, weight=1)

        top_bar = ttk.Frame(container, style="Hud.TFrame")
        top_bar.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        top_bar.grid_columnconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=1)
        top_bar.grid_columnconfigure(2, weight=1)

        left_sig = ttk.Label(top_bar, text="SYSTEM STATUS: OPERATIONAL", style="PanelText.TLabel")
        left_sig.configure(background="#02060F")
        left_sig.grid(row=0, column=0, sticky="w")

        title = ttk.Label(top_bar, text="ASHI CORE", style="HudTitle.TLabel")
        title.grid(row=0, column=1)

        right_sig = ttk.Label(top_bar, text="NEURAL LINK: ACTIVE", style="PanelText.TLabel")
        right_sig.configure(background="#02060F")
        right_sig.grid(row=0, column=2, sticky="e")

        self.left_panel = ttk.Frame(container, style="Panel.TFrame", padding=12)
        self.left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        self.center_panel = ttk.Frame(container, style="Hud.TFrame")
        self.center_panel.grid(row=1, column=1, sticky="nsew", padx=8)

        self.right_panel = ttk.Frame(container, style="Panel.TFrame", padding=12)
        self.right_panel.grid(row=1, column=2, sticky="nsew", padx=(8, 0))

        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> None:
        ttk.Label(self.left_panel, text="SYSTEM METRICS", style="PanelTitle.TLabel").pack(anchor="w")

        self.metric_cpu = tk.DoubleVar(value=0)
        self.metric_mem = tk.DoubleVar(value=0)
        self.metric_net = tk.DoubleVar(value=0)

        self.cpu_label = ttk.Label(self.left_panel, text="CPU: 0%", style="PanelText.TLabel")
        self.cpu_label.pack(anchor="w", pady=(8, 2))
        ttk.Progressbar(
            self.left_panel,
            variable=self.metric_cpu,
            maximum=100,
            style="Hud.Horizontal.TProgressbar",
        ).pack(fill="x")

        self.mem_label = ttk.Label(self.left_panel, text="MEMORY: 0%", style="PanelText.TLabel")
        self.mem_label.pack(anchor="w", pady=(8, 2))
        ttk.Progressbar(
            self.left_panel,
            variable=self.metric_mem,
            maximum=100,
            style="Hud.Horizontal.TProgressbar",
        ).pack(fill="x")

        self.net_label = ttk.Label(self.left_panel, text="NETWORK: 0%", style="PanelText.TLabel")
        self.net_label.pack(anchor="w", pady=(8, 2))
        ttk.Progressbar(
            self.left_panel,
            variable=self.metric_net,
            maximum=100,
            style="Hud.Horizontal.TProgressbar",
        ).pack(fill="x")

        ttk.Separator(self.left_panel).pack(fill="x", pady=12)

        ttk.Label(self.left_panel, text="VOICE CONTROL", style="PanelTitle.TLabel").pack(anchor="w")

        status_wrap = ttk.Frame(self.left_panel, style="Panel.TFrame")
        status_wrap.pack(fill="x", pady=(6, 8))
        self.mode_label = ttk.Label(status_wrap, text="Mode: system", style="PanelText.TLabel")
        self.mode_label.pack(anchor="w")
        self.voice_label = ttk.Label(status_wrap, text="Voice: Samantha", style="PanelText.TLabel")
        self.voice_label.pack(anchor="w")

        mode_wrap = ttk.Frame(self.left_panel, style="Panel.TFrame")
        mode_wrap.pack(fill="x", pady=(0, 8))
        ttk.Label(mode_wrap, text="Output Mode", style="PanelText.TLabel").pack(side="left")
        self.mode_var = tk.StringVar(value=self.assistant.memory.voice_mode())
        mode_combo = ttk.Combobox(
            mode_wrap,
            values=["system", "file", "clone"],
            state="readonly",
            textvariable=self.mode_var,
            width=10,
        )
        mode_combo.pack(side="right")
        mode_combo.bind("<<ComboboxSelected>>", lambda _e: self._submit_message(f"voice mode {self.mode_var.get()}"))

        ttk.Label(self.left_panel, text="SYSTEM VOICES", style="PanelText.TLabel").pack(anchor="w", pady=(2, 2))
        self.voice_list = tk.Listbox(
            self.left_panel,
            height=5,
            bg="#0A1A33",
            fg="#CBE8FF",
            selectbackground="#1E5C8A",
            borderwidth=0,
            highlightthickness=0,
            font=("Avenir Next", 10),
        )
        self.voice_list.pack(fill="x")

        voice_btn = ttk.Frame(self.left_panel, style="Panel.TFrame")
        voice_btn.pack(fill="x", pady=(4, 8))
        self._hud_button(voice_btn, "Refresh", self._load_voices, "#173D5D").pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._hud_button(voice_btn, "Use", self._set_selected_system_voice, "#1B5E8F").pack(side="left", fill="x", expand=True, padx=(4, 0))

        ttk.Label(self.left_panel, text="VOICE FILES (./save)", style="PanelText.TLabel").pack(anchor="w", pady=(2, 2))
        self.file_list = tk.Listbox(
            self.left_panel,
            height=4,
            bg="#0A1A33",
            fg="#CBE8FF",
            selectbackground="#1E5C8A",
            borderwidth=0,
            highlightthickness=0,
            font=("Avenir Next", 10),
        )
        self.file_list.pack(fill="x")

        file_btn = ttk.Frame(self.left_panel, style="Panel.TFrame")
        file_btn.pack(fill="x", pady=(4, 0))
        self._hud_button(file_btn, "Refresh", self._load_voice_files, "#173D5D").pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._hud_button(file_btn, "Use", self._set_selected_voice_file, "#1B5E8F").pack(side="left", fill="x", expand=True, padx=(4, 0))

        utility_btn = ttk.Frame(self.left_panel, style="Panel.TFrame")
        utility_btn.pack(fill="x", pady=(6, 0))
        self._hud_button(utility_btn, "Voice Input", self._run_voice_input_from_selected_file, "#295A7E").pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._hud_button(utility_btn, "Train Clone", self._train_clone_from_selected_file, "#2A7463").pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _build_center_panel(self) -> None:
        self.hud_canvas = tk.Canvas(
            self.center_panel,
            bg="#02060F",
            highlightthickness=0,
            borderwidth=0,
        )
        self.hud_canvas.pack(fill="both", expand=True)
        self.hud_canvas.bind("<Configure>", lambda _e: self._init_particles())

    def _build_right_panel(self) -> None:
        ttk.Label(self.right_panel, text="TACTICAL CONSOLE", style="PanelTitle.TLabel").pack(anchor="w")

        quick = ttk.Frame(self.right_panel, style="Panel.TFrame")
        quick.pack(fill="x", pady=(8, 10))

        actions = [
            ("Time", "time"),
            ("Date", "date"),
            ("Notes", "notes"),
            ("Help", "help"),
            ("Voice On", "voice on"),
            ("Voice Off", "voice off"),
        ]
        for idx, (label, cmd) in enumerate(actions):
            btn = self._hud_button(quick, label, lambda c=cmd: self._submit_message(c), "#183F66")
            btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=4)
        quick.grid_columnconfigure(0, weight=1)
        quick.grid_columnconfigure(1, weight=1)

        self.chat_box = tk.Text(
            self.right_panel,
            bg="#071426",
            fg="#CDEBFF",
            insertbackground="#CDEBFF",
            relief="flat",
            borderwidth=0,
            wrap="word",
            font=("Avenir Next", 11),
            state="disabled",
        )
        self.chat_box.pack(fill="both", expand=True)

        self.chat_box.tag_configure("user", foreground="#7FD8FF")
        self.chat_box.tag_configure("ashi", foreground="#E4F6FF")
        self.chat_box.tag_configure("meta", foreground="#5FA0C8")

        input_wrap = ttk.Frame(self.right_panel, style="Panel.TFrame")
        input_wrap.pack(fill="x", pady=(10, 0))

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_wrap,
            textvariable=self.input_var,
            bg="#0A1A33",
            fg="#E6F6FF",
            insertbackground="#E6F6FF",
            relief="flat",
            borderwidth=0,
            font=("Avenir Next", 12),
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda _e: self._submit_from_entry())

        self.send_button = self._hud_button(input_wrap, "Transmit", self._submit_from_entry, "#1D6CA3")
        self.send_button.pack(side="right")

    def _hud_button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#E9F6FF",
            activebackground="#2C7DB1",
            activeforeground="#FFFFFF",
            relief="flat",
            borderwidth=0,
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
        message = self.input_var.get().strip()
        if not message:
            return
        self.input_var.set("")
        self._submit_message(message)

    def _submit_message(self, message: str) -> None:
        self._post_user_message(message)
        self.send_button.configure(state="disabled")
        self.input_entry.configure(state="disabled")
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()

    def _process_message(self, message: str) -> None:
        reply = self.assistant.handle(message)
        self.root.after(0, lambda: self._finish_response(reply))

    def _finish_response(self, reply: str) -> None:
        if reply == self.assistant.EXIT_SIGNAL:
            self._post_bot_message("Goodbye.")
            self._speak_async("Goodbye.")
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
        self._append_chat("YOU", text, "user")

    def _post_bot_message(self, text: str) -> None:
        self._append_chat("ASHI", text, "ashi")

    def _append_chat(self, speaker: str, text: str, tag: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"[{timestamp}] ", "meta")
        self.chat_box.insert("end", f"{speaker}: ", tag)
        self.chat_box.insert("end", f"{text}\n\n", tag)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def _load_voices(self) -> None:
        self.voice_list.delete(0, tk.END)
        for voice in self.assistant.voice.available_system_voices(limit=80):
            self.voice_list.insert(tk.END, voice)

    def _load_voice_files(self) -> None:
        self.file_list.delete(0, tk.END)
        for name in self.assistant.voice.available_voice_files(limit=80):
            self.file_list.insert(tk.END, name)

    def _set_selected_system_voice(self) -> None:
        selection = self.voice_list.curselection()
        if not selection:
            return
        self._submit_message(f"voice {self.voice_list.get(selection[0])}")

    def _set_selected_voice_file(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            return
        self._submit_message(f"voicefile {self.file_list.get(selection[0])}")

    def _train_clone_from_selected_file(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            self._post_bot_message("Select an audio file first, then press Train Clone.")
            return
        filename = self.file_list.get(selection[0])
        self._submit_message(f"clonevoice {filename} ASHI Clone")

    def _run_voice_input_from_selected_file(self) -> None:
        selection = self.file_list.curselection()
        if not selection:
            self._post_bot_message("Select an audio file first, then press Voice Input.")
            return
        filename = self.file_list.get(selection[0])
        self._submit_message(f"listen {filename}")

    def _sync_status_labels(self) -> None:
        mode = self.assistant.memory.voice_mode()
        self.mode_label.configure(text=f"Mode: {mode}")

        if mode == "file":
            voice_name = self.assistant.memory.voice_file() or "(not set)"
        elif mode == "clone":
            voice_name = self.assistant.memory.clone_voice_name() or "(not set)"
        else:
            voice_name = self.assistant.memory.voice_name()
        self.voice_label.configure(text=f"Voice: {voice_name}")
        self.mode_var.set(mode)

    def _init_particles(self) -> None:
        width = max(self.hud_canvas.winfo_width(), 1)
        height = max(self.hud_canvas.winfo_height(), 1)
        if self._particles:
            return
        for _ in range(70):
            self._particles.append(
                {
                    "x": random.uniform(0, width),
                    "y": random.uniform(0, height),
                    "vx": random.uniform(-0.3, 0.3),
                    "vy": random.uniform(-0.3, 0.3),
                    "r": random.uniform(1.0, 2.4),
                }
            )

    def _get_metrics(self) -> tuple[float, float, float]:
        if self._psutil:
            cpu = float(self._psutil.cpu_percent(interval=None))
            mem = float(self._psutil.virtual_memory().percent)
            now = time.time()
            net = self._sim_net
            try:
                counters = self._psutil.net_io_counters()
                total = counters.bytes_sent + counters.bytes_recv
                if self._net_last_bytes is not None and self._net_last_time is not None:
                    delta_b = max(0, total - self._net_last_bytes)
                    delta_t = max(0.001, now - self._net_last_time)
                    rate = delta_b / delta_t
                    net = min(100.0, (rate / 900000.0) * 100.0)
                self._net_last_bytes = total
                self._net_last_time = now
            except Exception:
                pass
            return cpu, mem, net

        self._sim_cpu = max(8.0, min(94.0, self._sim_cpu + random.uniform(-3.2, 3.2)))
        self._sim_mem = max(12.0, min(91.0, self._sim_mem + random.uniform(-1.6, 1.6)))
        self._sim_net = max(4.0, min(99.0, self._sim_net + random.uniform(-4.8, 4.8)))
        return self._sim_cpu, self._sim_mem, self._sim_net

    def _draw_particles(self, width: int, height: int) -> None:
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0:
                p["x"] = width
            if p["x"] > width:
                p["x"] = 0
            if p["y"] < 0:
                p["y"] = height
            if p["y"] > height:
                p["y"] = 0
            self.hud_canvas.create_oval(
                p["x"] - p["r"],
                p["y"] - p["r"],
                p["x"] + p["r"],
                p["y"] + p["r"],
                fill="#57C9FF",
                outline="",
                tags="hud_dyn",
            )

    def _draw_hud_core(self, cpu: float, mem: float, net: float) -> None:
        width = self.hud_canvas.winfo_width()
        height = self.hud_canvas.winfo_height()
        cx = width / 2
        cy = height / 2

        self.hud_canvas.delete("hud_dyn")
        self._draw_particles(width, height)

        self.hud_canvas.create_line(0, cy, cx - 295, cy, fill="#12446B", width=1, tags="hud_dyn")
        self.hud_canvas.create_line(cx + 295, cy, width, cy, fill="#12446B", width=1, tags="hud_dyn")
        self.hud_canvas.create_line(cx, 0, cx, cy - 295, fill="#103B61", width=1, tags="hud_dyn")
        self.hud_canvas.create_line(cx, cy + 295, cx, height, fill="#103B61", width=1, tags="hud_dyn")

        rings = [290, 244, 192, 140, 92]
        for idx, r in enumerate(rings):
            color = "#0F3456" if idx % 2 == 0 else "#1A537F"
            self.hud_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=1, tags="hud_dyn")

        meter_specs = [
            (282, 35, cpu, "CPU", "#58D9FF"),
            (250, 158, mem, "MEM", "#5FC8FF"),
            (218, 281, net, "NET", "#68EEFF"),
        ]
        for radius, start, value, label, color in meter_specs:
            extent = (value / 100.0) * 260.0
            self.hud_canvas.create_arc(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                start=start,
                extent=extent,
                style="arc",
                outline=color,
                width=5,
                tags="hud_dyn",
            )
            self.hud_canvas.create_text(
                cx,
                cy - radius + 14,
                text=f"{label} {int(value)}%",
                fill="#8FE8FF",
                font=("Avenir Next", 10, "bold"),
                tags="hud_dyn",
            )

        glow = [
            (86, "#0E2744", 2),
            (72, "#124B70", 2),
            (60, "#1D7AAE", 2),
            (48, "#39B7E6", 2),
        ]
        for r, color, width_ring in glow:
            self.hud_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=width_ring, tags="hud_dyn")

        self.hud_canvas.create_oval(cx - 26, cy - 26, cx + 26, cy + 26, fill="#5DE7FF", outline="#B6F6FF", width=1, tags="hud_dyn")
        self.hud_canvas.create_text(cx, cy - 2, text="ASHI", fill="#02101E", font=("Avenir Next", 14, "bold"), tags="hud_dyn")
        self.hud_canvas.create_text(
            cx,
            cy + 30,
            text="ADVANCED STRATEGIC HUMAN INTERFACE",
            fill="#6FCFEA",
            font=("Avenir Next", 9),
            tags="hud_dyn",
        )

    def _animate_hud(self) -> None:
        cpu, mem, net = self._get_metrics()
        self.metric_cpu.set(cpu)
        self.metric_mem.set(mem)
        self.metric_net.set(net)
        self.cpu_label.configure(text=f"CPU: {int(cpu)}%")
        self.mem_label.configure(text=f"MEMORY: {int(mem)}%")
        self.net_label.configure(text=f"NETWORK: {int(net)}%")
        self._draw_hud_core(cpu, mem, net)
        self.root.after(120, self._animate_hud)


def run_gui() -> None:
    root = tk.Tk()
    app = AashiDashboardApp(root)
    app.input_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    run_gui()

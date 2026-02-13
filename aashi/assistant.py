import os
from typing import Optional

from .ai import AIResponder
from .clone_voice import CloneVoiceEngine
from .config import AppConfig
from .env_loader import load_local_env_files
from .memory import MemoryStore
from .pipeline import AIBrain, InputLayer, IntentRouter, ResponseGenerator, TaskPlanner, ToolExecutor
from .system_control import SystemController
from .voice import VoiceEngine
from .voice_input import VoiceInputEngine


class AashiAssistant:
    EXIT_SIGNAL = "EXIT"

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        memory: Optional[MemoryStore] = None,
        voice: Optional[VoiceEngine] = None,
        ai: Optional[AIResponder] = None,
        clone_voice: Optional[CloneVoiceEngine] = None,
        voice_input: Optional[VoiceInputEngine] = None,
        system_control: Optional[SystemController] = None,
    ) -> None:
        load_local_env_files()
        self.config = config or AppConfig.from_env()

        self.memory = memory or MemoryStore(self.config.memory_file)
        self.voice = voice or VoiceEngine(self.config.voice_files_dir)
        self.ai = ai or AIResponder(
            model=self.config.openai_model,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.clone_voice = clone_voice or CloneVoiceEngine(
            voice_files_dir=self.config.voice_files_dir,
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )
        self.voice_input = voice_input or VoiceInputEngine(
            voice_files_dir=self.config.voice_files_dir,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.system_control = system_control or SystemController()

        self.input_layer = InputLayer()
        self.router = IntentRouter()
        self.brain = AIBrain(self.ai)
        self.planner = TaskPlanner()
        self.tool_executor = ToolExecutor(self)
        self.response_generator = ResponseGenerator()

    def greet(self) -> str:
        return (
            "Hi, I am ASHI. Advanced Strategic Human Interface is online. "
            "Type 'help' to see what I can do."
        )

    def help_text(self) -> str:
        return (
            "Commands: help, time, date, notes, save <text>, voices, voice <name>, voice on, voice off,\n"
            "voice mode <system|file|clone>, voicefiles, voicefile <filename>, listen <filename>,\n"
            "clonevoice <filename> [name], clone status, clone say <text>,\n"
            "wake on, wake off, wake status, wake phrase <text>,\n"
            "setup openai, setup elevenlabs, setup status,\n"
            "open app <name>, open web <url>, search web <query>, run shortcut <name>, exit\n"
            "You can also ask normal questions."
        )

    def handle(self, user_input: str) -> str:
        packet = self.input_layer.prepare(user_input)
        if not packet.text:
            return "Say something and I will help."

        intent = self.router.route(packet.text)
        plan = self.planner.plan(intent)

        last_result = None
        for action in plan.actions:
            last_result = self.tool_executor.execute(action)

        if last_result is None:
            return "I could not process that request."

        return self.response_generator.generate(last_result)

    def speak(self, text: str) -> None:
        if not self.memory.voice_enabled():
            return

        mode = self.memory.voice_mode()
        if mode == "clone":
            self.clone_voice.speak(text, self.memory.clone_voice_id())
            return

        if mode == "file":
            self.voice.play_file(self.memory.voice_file())
            return

        self.voice.speak_system(self.memory.voice_name(), text)

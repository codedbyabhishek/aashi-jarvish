import re
import shutil
import subprocess
from urllib.parse import quote_plus


class SystemController:
    def open_app(self, app_name: str) -> tuple[bool, str]:
        app_name = app_name.strip()
        if not app_name:
            return False, "Use: open app <AppName>"

        if not shutil.which("open"):
            return False, "System open command is not available."

        try:
            result = subprocess.run(["open", "-a", app_name], capture_output=True, text=True, check=False)
        except OSError:
            return False, "Failed to open app."

        if result.returncode != 0:
            return False, f"Could not open app '{app_name}'."

        return True, f"Opened app '{app_name}'."

    def open_url(self, raw: str) -> tuple[bool, str]:
        target = raw.strip()
        if not target:
            return False, "Use: open web <url>"

        if not target.startswith(("http://", "https://")):
            target = f"https://{target}"

        if not shutil.which("open"):
            return False, "System open command is not available."

        try:
            result = subprocess.run(["open", target], capture_output=True, text=True, check=False)
        except OSError:
            return False, "Failed to open URL."

        if result.returncode != 0:
            return False, "Could not open URL."

        return True, f"Opened {target}"

    def search_web(self, query: str) -> tuple[bool, str]:
        q = query.strip()
        if not q:
            return False, "Use: search web <query>"

        url = f"https://www.google.com/search?q={quote_plus(q)}"
        return self.open_url(url)

    def run_shortcut(self, name: str) -> tuple[bool, str]:
        shortcut_name = name.strip()
        if not shortcut_name:
            return False, "Use: run shortcut <name>"

        if not shutil.which("shortcuts"):
            return False, "Apple Shortcuts CLI is not available."

        try:
            result = subprocess.run(
                ["shortcuts", "run", shortcut_name],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            return False, "Failed to run shortcut."

        if result.returncode != 0:
            return False, f"Shortcut '{shortcut_name}' failed or was not found."

        return True, f"Ran shortcut '{shortcut_name}'."

    def try_natural_action(self, text: str) -> tuple[bool, str]:
        cmd = text.strip()
        lower = cmd.lower()

        if lower.startswith("open app "):
            return self.open_app(cmd[9:])

        if lower.startswith("open web "):
            return self.open_url(cmd[9:])

        if lower.startswith("search web "):
            return self.search_web(cmd[11:])

        if lower.startswith("run shortcut "):
            return self.run_shortcut(cmd[13:])

        open_app_match = re.match(r"^open\s+([a-zA-Z0-9 ._-]+)$", cmd, re.IGNORECASE)
        if open_app_match:
            return self.open_app(open_app_match.group(1))

        return False, ""

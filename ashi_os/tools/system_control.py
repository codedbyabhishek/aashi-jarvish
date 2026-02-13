import shutil
import subprocess


class SystemControlModule:
    def open_app(self, app_name: str) -> dict:
        app_name = app_name.strip()
        if not app_name:
            return {"ok": False, "message": "app_name is required."}

        if not shutil.which("open"):
            return {"ok": False, "message": "System open command not available."}

        result = subprocess.run(["open", "-a", app_name], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return {"ok": False, "message": f"Failed to open app '{app_name}'."}
        return {"ok": True, "message": f"Opened app '{app_name}'."}

    def run_shortcut(self, shortcut_name: str) -> dict:
        shortcut_name = shortcut_name.strip()
        if not shortcut_name:
            return {"ok": False, "message": "shortcut_name is required."}

        if not shutil.which("shortcuts"):
            return {"ok": False, "message": "Shortcuts CLI is not available."}

        result = subprocess.run(["shortcuts", "run", shortcut_name], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return {"ok": False, "message": f"Failed to run shortcut '{shortcut_name}'."}
        return {"ok": True, "message": f"Ran shortcut '{shortcut_name}'.", "stdout": result.stdout.strip()}

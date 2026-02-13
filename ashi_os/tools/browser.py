import shutil
import subprocess
from urllib.parse import quote_plus


class BrowserModule:
    def open_url(self, url: str) -> dict:
        if not url.startswith(("http://", "https://")):
            return {"ok": False, "message": "URL must start with http:// or https://"}

        if not shutil.which("open"):
            return {"ok": False, "message": "System open command not available."}

        result = subprocess.run(["open", url], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return {"ok": False, "message": "Failed to open URL."}
        return {"ok": True, "message": "Opened URL.", "url": url}

    def search_web(self, query: str) -> dict:
        query = query.strip()
        if not query:
            return {"ok": False, "message": "query is required."}
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        return self.open_url(url)

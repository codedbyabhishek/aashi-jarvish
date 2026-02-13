from pathlib import Path


class FileSystemModule:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root.resolve()

    def list_dir(self, rel_path: str = ".") -> dict:
        target = self._resolve(rel_path)
        if not target.exists() or not target.is_dir():
            return {"ok": False, "message": "Directory not found."}

        entries = []
        for child in sorted(target.iterdir()):
            entries.append(
                {
                    "name": child.name,
                    "kind": "dir" if child.is_dir() else "file",
                    "size": child.stat().st_size if child.is_file() else None,
                }
            )
        return {"ok": True, "path": str(target), "entries": entries}

    def read_file(self, rel_path: str, max_chars: int = 20000) -> dict:
        target = self._resolve(rel_path)
        if not target.exists() or not target.is_file():
            return {"ok": False, "message": "File not found."}

        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"ok": False, "message": "File is not UTF-8 text."}

        return {
            "ok": True,
            "path": str(target),
            "content": content[:max_chars],
            "truncated": len(content) > max_chars,
        }

    def write_file(self, rel_path: str, content: str, append: bool = False) -> dict:
        target = self._resolve(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with target.open(mode, encoding="utf-8") as handle:
            handle.write(content)
        return {"ok": True, "path": str(target)}

    def mkdir(self, rel_path: str) -> dict:
        target = self._resolve(rel_path)
        target.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "path": str(target)}

    def delete_path(self, rel_path: str) -> dict:
        target = self._resolve(rel_path)
        if not target.exists():
            return {"ok": False, "message": "Path not found."}
        if target.is_dir():
            return {"ok": False, "message": "Directory deletion is disabled."}
        target.unlink()
        return {"ok": True, "path": str(target)}

    def _resolve(self, rel_path: str) -> Path:
        candidate = (self.workspace_root / rel_path).resolve()
        if self.workspace_root != candidate and self.workspace_root not in candidate.parents:
            raise PermissionError("Path escapes workspace root.")
        return candidate

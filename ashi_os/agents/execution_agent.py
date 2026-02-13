from ashi_os.tools.executor import ToolExecutor


class ExecutionAgent:
    def __init__(self, tool_executor: ToolExecutor) -> None:
        self.tool_executor = tool_executor

    def propose_actions(self, plan_steps: list[dict]) -> list[dict]:
        actions: list[dict] = []
        for step in plan_steps:
            task = str(step.get("task", "")).strip()
            lower = task.lower()

            if lower.startswith("open app "):
                actions.append({"tool": "system", "action": "open_app", "params": {"app_name": task[9:].strip()}})
            elif lower.startswith("open web "):
                actions.append({"tool": "browser", "action": "open_url", "params": {"url": task[9:].strip()}})
            elif lower.startswith("search web "):
                actions.append({"tool": "browser", "action": "search_web", "params": {"query": task[11:].strip()}})
            elif lower.startswith("list files") or lower.startswith("list dir"):
                actions.append({"tool": "filesystem", "action": "list", "params": {"path": "."}})
            elif lower.startswith("read file "):
                actions.append({"tool": "filesystem", "action": "read", "params": {"path": task[10:].strip()}})
            elif lower.startswith("write file "):
                # Format: write file path::content
                payload = task[11:].strip()
                if "::" in payload:
                    path, content = payload.split("::", 1)
                    actions.append(
                        {
                            "tool": "filesystem",
                            "action": "write",
                            "params": {"path": path.strip(), "content": content},
                        }
                    )
            elif lower.startswith("run command "):
                actions.append({"tool": "code", "action": "run", "params": {"command": task[12:].strip()}})

        return actions

    def execute(self, session_id: str, actions: list[dict], confirm: bool = False) -> list[dict]:
        results = []
        for index, action in enumerate(actions, start=1):
            result = self.tool_executor.execute(
                session_id=session_id,
                tool=action["tool"],
                action=action["action"],
                params=action.get("params", {}),
                confirm=confirm,
            )
            results.append({"step": index, "action": action, "result": result})
        return results


class ValidationAgent:
    def run(self, execution_results: list[dict], auto_execute: bool) -> dict:
        if not auto_execute:
            return {
                "ok": True,
                "summary": "Dry-run mode. No tool actions executed.",
                "success_count": 0,
                "failure_count": 0,
            }

        success = 0
        failure = 0
        errors = []

        for item in execution_results:
            result = item.get("result", {})
            if result.get("ok"):
                success += 1
            else:
                failure += 1
                errors.append(result.get("message", "Unknown failure"))

        summary = f"Executed {success + failure} actions: {success} succeeded, {failure} failed."
        return {
            "ok": failure == 0,
            "summary": summary,
            "success_count": success,
            "failure_count": failure,
            "errors": errors,
        }

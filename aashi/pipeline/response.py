from .types import ExecutionResult


class ResponseGenerator:
    def generate(self, result: ExecutionResult) -> str:
        return result.message

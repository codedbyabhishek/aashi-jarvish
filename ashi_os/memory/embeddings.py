from typing import Protocol


class EmbeddingProvider(Protocol):
    def name(self) -> str: ...


class DefaultEmbeddingProvider:
    def name(self) -> str:
        return "chroma_default"

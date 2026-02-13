from typing import Any

from ashi_os.core.config import Settings


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None
        self._collection = None
        self._ready = False

    def _init_client(self) -> None:
        if self._ready:
            return
        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self.settings.chroma_dir))
            self._collection = self._client.get_or_create_collection(name="ashi_memory")
            self._ready = True
        except Exception:
            self._client = None
            self._collection = None
            self._ready = True

    def add(self, doc_id: str, text: str, metadata: dict[str, Any]) -> None:
        self._init_client()
        if self._collection is None:
            return
        self._collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])

    def query(self, query_text: str, top_k: int) -> list[dict[str, Any]]:
        self._init_client()
        if self._collection is None:
            return []
        result = self._collection.query(query_texts=[query_text], n_results=top_k)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        ids = result.get("ids", [[]])[0]
        hits = []
        for idx, text in enumerate(docs):
            hits.append(
                {
                    "id": ids[idx] if idx < len(ids) else "",
                    "text": text,
                    "metadata": metas[idx] if idx < len(metas) else {},
                }
            )
        return hits

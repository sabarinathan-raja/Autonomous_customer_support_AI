
import chromadb
from pathlib import Path


class VectorStore:

    def __init__(
        self,
        persist_directory="data/vectorstore",
        collection_name="customer_support_policies"
    ):

        Path(persist_directory).mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents, embeddings):

        if not documents:
            return

        ids = [
            f"{doc['source']}::chunk::{doc['chunk_id']}"
            for doc in documents
        ]

        self.collection.upsert(
            ids=ids,
            documents=[doc["text"] for doc in documents],
            embeddings=embeddings,
            metadatas=[
                {
                    "source": doc["source"],
                    "chunk_id": doc["chunk_id"]
                }
                for doc in documents
            ]
        )

    def search(self, query_embedding, top_k=5):

        if self.collection.count() == 0:
            return []

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )

        documents = result["documents"][0] or []
        metadatas = result["metadatas"][0] or []
        distances = result["distances"][0] or []

        return [
            {
                "text": document,
                "source": metadata["source"],
                "distance": distance
            }
            for document, metadata, distance
            in zip(documents, metadatas, distances)
        ]

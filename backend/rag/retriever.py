
from backend.rag.document_loader import DocumentLoader
from backend.rag.chunking import TextChunker
from backend.rag.embeddings import EmbeddingService
from backend.rag.vectorstore import VectorStore
from backend.rag.reranker import DocumentReranker


class PolicyRetriever:

    def __init__(self):

        self.loader = DocumentLoader()

        self.chunker = TextChunker(
            chunk_size=500,
            overlap=100
        )

        self.embedding_service = EmbeddingService()

        self.vectorstore = VectorStore()

        self.reranker = DocumentReranker()

        self.ingest_documents()

    def ingest_documents(self):

        documents = self.loader.load_documents()

        chunks = self.chunker.process_documents(
            documents
        )

        if not chunks:
            return 0

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.embedding_service.embed_documents(
            texts
        )

        self.vectorstore.add_documents(
            chunks,
            embeddings
        )

        return len(chunks)

    def search(self, query, top_k=5):

        query_embedding = self.embedding_service.embed_query(
            query
        )

        results = self.vectorstore.search(
            query_embedding,
            top_k=top_k
        )

        return self.reranker.rerank(
            query,
            results,
            top_k=3
        )

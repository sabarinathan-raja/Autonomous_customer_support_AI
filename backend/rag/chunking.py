
class TextChunker:

    def __init__(self, chunk_size=500, overlap=100):

        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text):

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):

            end = start + self.chunk_size

            chunk = " ".join(words[start:end])

            if chunk.strip():
                chunks.append(chunk)

            if end >= len(words):
                break

            start = end - self.overlap

        return chunks

    def process_documents(self, documents):

        results = []

        for document in documents:

            chunks = self.split_text(document["text"])

            for index, chunk in enumerate(chunks):

                results.append({
                    "text": chunk,
                    "source": document["source"],
                    "chunk_id": index
                })

        return results

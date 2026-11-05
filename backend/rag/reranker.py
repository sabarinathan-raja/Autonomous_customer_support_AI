
class DocumentReranker:

    def rerank(self, query, documents, top_k=3):

        query_words = set(query.lower().split())

        scored_documents = []

        for document in documents:

            text_words = set(
                document["text"].lower().split()
            )

            score = len(query_words & text_words)

            scored_documents.append({
                **document,
                "rerank_score": score
            })

        scored_documents.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return scored_documents[:top_k]

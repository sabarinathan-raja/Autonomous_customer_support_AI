
from backend.rag.retriever import PolicyRetriever


def test_policy_retrieval():

    retriever = PolicyRetriever()

    query = "What are the refund eligibility rules?"

    results = retriever.search(query, top_k=5)

    assert isinstance(results, list)

    assert len(results) > 0

    print("\nRAG Retrieval Results:\n")

    for index, result in enumerate(results, 1):

        print(f"Result {index}")

        print("Source:", result["source"])

        print("Content:", result["text"])

        print("Rerank Score:", result["rerank_score"])

        print("-" * 50)


if __name__ == "__main__":

    test_policy_retrieval()

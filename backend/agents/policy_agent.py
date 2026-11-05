
from backend.rag.retriever import PolicyRetriever


class PolicyAgent:

    def __init__(self):
        self.retriever = PolicyRetriever()

    def retrieve_policy(self, query: str):

        results = self.retriever.search(query)

        return {
            "query": query,
            "evidence": results,
            "evidence_available": bool(results)
        }

from src.retrieval.hybrid_retriever import HybridRetriever
from src.generation.generator import ResponseGenerator

class GraphRAGPipeline:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.generator = ResponseGenerator()
        
    def query(self, user_query: str) -> str:
        """
        End-to-end RAG pipeline execution.
        """
        # 1. Retrieve subgraph and evidence context
        context = self.retriever.retrieve(user_query)
        
        # 2. Generate final response using LLM
        response = self.generator.generate(user_query, context)
        
        return response

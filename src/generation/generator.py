from langchain_community.chat_models import ChatOpenAI
from src.config import settings
from src.generation.prompts import graph_rag_prompt
from langchain_core.output_parsers import StrOutputParser

class ResponseGenerator:
    def __init__(self):
        # We configure ChatOpenAI to point to the open model API endpoint
        self.llm = ChatOpenAI(
            openai_api_base=settings.llm_base_url,
            openai_api_key=settings.llm_api_key,
            model_name=settings.llm_model_name
        )
        self.chain = graph_rag_prompt | self.llm | StrOutputParser()
        
    def generate(self, query: str, context: str) -> str:
        """
        Passes the query and graph context to the LLM to generate the final response.
        """
        return self.chain.invoke({"query": query, "context": context})

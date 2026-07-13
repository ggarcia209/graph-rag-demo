from langchain_core.prompts import PromptTemplate

GRAPH_RAG_PROMPT_TEMPLATE = """
You are a financial and geopolitical analyst agent.
You have been provided with the following evidence extracted from a knowledge graph of events, organizations, and markets.

Knowledge Graph Evidence:
{context}

Answer the following user query based ONLY on the provided evidence. If the evidence does not contain the answer, say "I don't have enough information."

User Query: {query}
Answer:
"""

graph_rag_prompt = PromptTemplate(
    input_variables=["context", "query"],
    template=GRAPH_RAG_PROMPT_TEMPLATE
)

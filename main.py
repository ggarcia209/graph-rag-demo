import sys
from src.pipeline import GraphRAGPipeline

def main():
    print("Initializing Graph RAG Pipeline...")
    
    try:
        pipeline = GraphRAGPipeline()
    except Exception as e:
        print(f"Failed to initialize pipeline (check your .env settings): {e}")
        sys.exit(1)
        
    sample_query = "How would a military conflict near the Strait of Hormuz affect Delta Air Lines stock?"
    print(f"\nRunning Query: {sample_query}")
    
    try:
        response = pipeline.query(sample_query)
        print("\n--- Pipeline Response ---")
        print(response)
    except Exception as e:
        print(f"\nPipeline query failed (this is expected if LLM or DB isn't running yet): {e}")

if __name__ == "__main__":
    main()

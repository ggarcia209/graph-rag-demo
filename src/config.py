from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    falkordb_host: str = "localhost"
    falkordb_port: int = 6379
    falkordb_password: str = ""

    llm_base_url: str = "http://localhost:8000/v1"
    llm_api_key: str = "your-api-key-here"
    llm_model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    embedding_model_name: str = "Qwen/Qwen3-Embedding"

    class Config:
        env_file = ".env"

settings = Settings()

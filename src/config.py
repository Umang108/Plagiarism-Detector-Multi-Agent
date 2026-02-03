import os
from dotenv import load_dotenv
from typing import Literal

from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import OllamaEmbeddings

load_dotenv()

class Config:
    OPENAI_MODEL: Literal[
        "gpt-4o-mini",
        "gpt_35_turbo_0613"
    ] = os.getenv("OPENAI_MODEL", "gpt_35_turbo_0613")

    
    EMBEDDING_MODEL = "all-minilm:latest"

    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

    SIMILARITY_THRESHOLD = 0.75
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 200
    MAX_INTERNET_PAPERS = 5
    MAX_CONCEPTS = 40  # Default limit for extracted concepts
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

config = Config()

# -------------------------------
# Azure OpenAI LLM (MODIFIED)
# -------------------------------
llm = AzureChatOpenAI(
    deployment_name=config.OPENAI_MODEL,
    temperature=0.7,
    validate_base_url=False
)


# -------------------------------
# all-MiniLM Embeddings (Ollama)
# -------------------------------
text_embeddings = OllamaEmbeddings(
    model=config.EMBEDDING_MODEL
)

verify_ssl = config.VERIFY_SSL

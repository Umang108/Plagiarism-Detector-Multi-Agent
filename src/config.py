import os
from dotenv import load_dotenv
from typing import Literal

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings  # kept as-is

load_dotenv()

class Config:
    OPENAI_MODEL: Literal[
        "gpt-4o-mini",
        "gpt_35_turbo_0613"
    ] = os.getenv("OPENAI_MODEL", "gpt_35_turbo_0613")

    # Azure-supported embedding model
    EMBEDDING_MODEL = "text-embedding-3-small"

    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-02-01")

    SIMILARITY_THRESHOLD = 0.75
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 200
    MAX_INTERNET_PAPERS = 5
    MAX_CONCEPTS = 40
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

config = Config()

# -------------------------------
# Azure OpenAI LLM
# -------------------------------
llm = AzureChatOpenAI(
    azure_deployment=config.OPENAI_MODEL,   # ✅ corrected
    api_version=config.OPENAI_API_VERSION,
    temperature=0.7,
    validate_base_url=False
)

# -------------------------------
# Azure OpenAI Embeddings
# -------------------------------
text_embeddings = AzureOpenAIEmbeddings(
    azure_deployment="TEA",                # embedding deployment name
    model=config.EMBEDDING_MODEL,
    api_version=config.OPENAI_API_VERSION
)

verify_ssl = config.VERIFY_SSL

from langchain_community.utilities import ArxivAPIWrapper
from tavily import TavilyClient
from langchain_core.tools import tool
from typing import List, Dict
from src.config import config


class AdvancedResearchSearcher:
    def __init__(self):
        self.arxiv = ArxivAPIWrapper(
            top_k_results=5,
            load_max_docs=5
        )
        self.tavily = TavilyClient(api_key=config.TAVILY_API_KEY)

    def search_research_papers(
        self,
        title: str,
        abstract: str
    ) -> List[Dict]:
        """
        Robust multi-source research paper search
        Returns structured paper metadata
        """

        papers: List[Dict] = []

        # --------------------
        # 1️⃣ Arxiv (PRIMARY)
        # --------------------
        try:
            arxiv_query = " ".join(title.split()[:6])
            arxiv_docs = self.arxiv.get_docs(arxiv_query)

            for doc in arxiv_docs:
                papers.append({
                    "title": doc.metadata.get("Title", ""),
                    "url": doc.metadata.get("Entry ID", ""),
                    "snippet": doc.page_content[:300],
                    "source": "arxiv"
                })
        except Exception as e:
            print("Arxiv search failed:", e)

        # --------------------
        # 2️⃣ Tavily (SEMANTIC)
        # --------------------
        try:
            semantic_query = f"{title} {abstract[:200]}"
            tavily_results = self.tavily.search(
                query=semantic_query,
                max_results=5,
                include_domains=["arxiv.org", "neurips.cc", "openreview.net"]
            )

            for r in tavily_results.get("results", []):
                papers.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:300],
                    "source": "web"
                })
        except Exception as e:
            print("Tavily search failed:", e)

        # --------------------
        # 3️⃣ Deduplicate & Filter
        # --------------------
        unique = {}
        for p in papers:
            if p["url"] and p["url"] not in unique:
                unique[p["url"]] = p

        return list(unique.values())[:config.MAX_INTERNET_PAPERS]


research_searcher = AdvancedResearchSearcher()


@tool
def search_research_papers_tool(title: str, abstract: str) -> List[Dict]:
    """Search academic papers from Arxiv and web"""
    return research_searcher.search_research_papers(title, abstract)

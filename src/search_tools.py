from langchain_community.retrievers import ArxivRetriever
from tavily import TavilyClient
from langchain_core.tools import tool
from typing import List, Dict
from src.config import config

TAVILY_API_KEY = "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"
class AdvancedResearchSearcher:
    def __init__(self):
        self.arxiv = ArxivRetriever(
            load_max_docs=5,
            get_full_documents=True,
        )
        self.tavily = TavilyClient(api_key=TAVILY_API_KEY)

    def extract_title_and_abstract(self, text: str):
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        title = "N/A"
        abstract = ""

        # Try to find ABSTRACT marker
        for i, line in enumerate(lines):
            if line.lower().startswith("abstract"):
                title = lines[i - 1] if i > 0 else lines[0]
                abstract = " ".join(lines[i + 1:i + 10])
                break

        # Fallback
        if title == "N/A" and lines:
            title = lines[0]
            abstract = " ".join(lines[1:10])

        return title, abstract

    def search_research_papers(self, title: str, abstract: str) -> List[Dict]:
        papers: List[Dict] = []

        # --------------------
        # 1️⃣ Arxiv
        # --------------------
        try:
            arxiv_docs = self.arxiv.invoke(title)

            print("\n========== ARXIV RESULTS ==========\n")

            with open("data.txt", "w", encoding="utf-8") as f:
                f.write(str(arxiv_docs))

            for i, doc in enumerate(arxiv_docs, start=1):
                text = doc.page_content
                meta = doc.metadata or {}

                paper_title, paper_abstract = self.extract_title_and_abstract(text)

                print(f"[{i}] TITLE: {paper_title}")
                print(f"[{i}] ABSTRACT:\n{paper_abstract[:500]}")
                print("-" * 80)

                papers.append({
                    "title": paper_title,
                    "url": meta.get("entry_id") or meta.get("source", ""),
                    "authors": meta.get("authors", []),
                    "published": meta.get("published", ""),
                    "snippet": paper_abstract[:300],
                    "source": "arxiv"
                })

        except Exception as e:
            print("Arxiv search failed:", e)

        # --------------------
        # 2️⃣ Tavily
        # --------------------
        try:
            semantic_query = f"{title} {abstract}"
            tavily_results = self.tavily.search(
                query=semantic_query,
                max_results=5,
                include_domains=[
                    "arxiv.org",
                    "neurips.cc",
                    "openreview.net",
                    "paperswithcode.com"
                ]
            )

            for r in tavily_results.get("results", []):
                papers.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "authors": [],
                    "published": "",
                    "snippet": r.get("content", "")[:300],
                    "source": "web"
                })

        except Exception as e:
            print("Tavily search failed:", e)

        # --------------------
        # 3️⃣ Dedup
        # --------------------
        unique = {}
        for p in papers:
            if p.get("url") and p["url"] not in unique:
                unique[p["url"]] = p

        return list(unique.values())[:config.MAX_INTERNET_PAPERS]

# Singleton instance
research_searcher = AdvancedResearchSearcher()


@tool
def search_research_papers_tool(title: str, abstract: str) -> List[Dict]:
    """
    Search academic papers from Arxiv and web sources.
    """
    return research_searcher.search_research_papers(title, abstract)

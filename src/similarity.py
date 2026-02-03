from langchain_community.vectorstores.faiss import FAISS
from src.config import text_embeddings, config
from models.paper_struct import Concept
from typing import List, Dict
import numpy as np


class AdvancedSemanticMatcher:
    def __init__(self):
        self.user_store: FAISS | None = None
        self.internet_stores: Dict[str, FAISS] = {}

    # -------------------------------------------------
    # Embed concepts into FAISS
    # -------------------------------------------------
    def embed_concepts(self, concepts: List[Concept], identifier: str):
        """Embed concepts into FAISS vector store"""
        if not concepts:
            return

        texts = []
        for c in concepts:
            text = (
                f"{c.name} | {c.description} | "
                f"section:{c.section} | type:{c.type.value}"
            )
            texts.append(text)

        vectorstore = FAISS.from_texts(texts, text_embeddings)

        if identifier == "user":
            self.user_store = vectorstore
        else:
            self.internet_stores[identifier] = vectorstore

    # -------------------------------------------------
    # Cross-paper similarity analysis
    # -------------------------------------------------
    def cross_similarity_analysis(
        self,
        similarity_threshold: float = 0.75
    ) -> Dict[str, List[Dict]]:
        """Compare user concepts with internet paper concepts"""

        if not self.user_store:
            raise ValueError("User concepts must be embedded first")

        results: Dict[str, List[Dict]] = {}

        # All user concept documents
        user_docs = list(self.user_store.docstore._dict.values())

        for paper_id, store in self.internet_stores.items():
            matches: List[Dict] = []

            for user_doc in user_docs:
                similar_docs = store.similarity_search_with_score(
                    user_doc.page_content,
                    k=8
                )

                for doc, distance in similar_docs:
                    # ✅ Correct similarity computation
                    similarity = max(0.0, 1 - distance)

                    if similarity < similarity_threshold:
                        continue

                    # Section-aware tagging
                    section = (
                        "methodology"
                        if "method" in user_doc.page_content.lower()
                        or "algorithm" in user_doc.page_content.lower()
                        else "other"
                    )

                    matches.append({
                        "user_concept": user_doc.page_content,
                        "matched_concept": doc.page_content,
                        "similarity_score": round(similarity, 3),
                        "section": section,
                        "match_strength": (
                            "STRONG" if similarity > 0.85 else
                            "MEDIUM" if similarity > 0.75 else
                            "WEAK"
                        )
                    })

            # Limit matches per paper
            results[paper_id] = matches[:10]

        return results

    # -------------------------------------------------
    # Aggregate scoring & novelty computation
    # -------------------------------------------------
    def compute_aggregate_scores(
        self,
        matches_by_paper: Dict[str, List[Dict]]
    ) -> Dict:
        """Compute plagiarism risk & novelty score"""

        paper_scores = {}
        total_high_risk_matches = 0

        for paper_id, matches in matches_by_paper.items():
            if not matches:
                continue

            clean_matches = [
                m for m in matches
                if isinstance(m, dict)
                and isinstance(m.get("similarity_score"), (int, float))
            ]

            if not clean_matches:
                continue

            # ✅ Section-weighted similarity
            weighted_scores = []
            for m in clean_matches:
                weight = 1.5 if m.get("section") == "methodology" else 1.0
                weighted_scores.append(m["similarity_score"] * weight)

            avg_similarity = float(np.mean(weighted_scores))
            high_risk_count = sum(
                1 for m in clean_matches if m["similarity_score"] > 0.85
            )

            total_high_risk_matches += high_risk_count

            paper_scores[paper_id] = {
                "overlap_percentage": round(avg_similarity * 100, 1),
                "high_risk_matches": high_risk_count,
                "total_matches": len(clean_matches),
                "risk_category": (
                    "CRITICAL" if avg_similarity > 0.9 else
                    "HIGH" if avg_similarity > 0.8 else
                    "MEDIUM" if avg_similarity > 0.7 else
                    "LOW"
                )
            }

        # -------------------------------------------------
        # Safe handling when no papers matched
        # -------------------------------------------------
        if not paper_scores:
            return {
                "overall_overlap_pct": None,
                "novelty_score": None,
                "total_papers_analyzed": 0,
                "total_high_risk_matches": 0,
                "paper_breakdown": {},
                "risk_assessment": "UNKNOWN"
            }

        overall_overlap = float(
            np.mean([ps["overlap_percentage"] for ps in paper_scores.values()])
        )
        novelty_score = max(0.0, 100.0 - overall_overlap)

        return {
            "overall_overlap_pct": round(overall_overlap, 1),
            "novelty_score": round(novelty_score, 1),
            "total_papers_analyzed": len(paper_scores),
            "total_high_risk_matches": total_high_risk_matches,
            "paper_breakdown": paper_scores,
            "risk_assessment": (
                "HIGH" if overall_overlap > 60 else
                "MEDIUM" if overall_overlap > 30 else
                "LOW"
            )
        }

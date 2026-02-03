from pydantic import BaseModel, Field
from typing import List, Dict, Optional  # ✅ ADDED MISSING IMPORT
from datetime import datetime
from .paper_struct import Concept  # ✅ Relative import

class InternetMatch(BaseModel):
    paper_title: str
    paper_url: str
    source: str
    overlap_pct: float
    core_concepts_overlap: int
    matching_concepts: List[Dict[str, str]]
    publication_year: Optional[int] = None  # ✅ Now works!

class Explainability(BaseModel):
    top_contributing_phrases: List[str]
    attention_weights: Dict[str, float]
    false_positives_filtered: int

class AnalysisResult(BaseModel):
    submitted_paper_title: str
    total_internet_papers_analyzed: int
    top_similar_papers: List[InternetMatch]
    overall_plagiarism_risk: str  # LOW/MEDIUM/HIGH
    novelty_score: float  # 0-100
    temporal_risk_multiplier: float = 1.0
    explainability: Explainability
    recommendations: List[str]
    detailed_report: str
    processed_at: str

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
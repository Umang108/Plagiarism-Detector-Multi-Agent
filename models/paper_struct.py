from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

# Rest of your existing code...
class ConceptType(str, Enum):
    ALGORITHM = "algorithm"
    TECHNIQUE = "technique" 
    DOMAIN = "domain"
    METRIC = "metric"
    DATASET = "dataset"
    EQUATION = "equation"
    FIGURE = "figure"
    CITATION = "citation"
    TABLE = "table"


class Concept(BaseModel):
    name: str
    type: ConceptType
    description: str
    section: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    visual_embedding: Optional[List[float]] = None

class PaperSection(BaseModel):
    content: str
    page_numbers: List[int]
    word_count: int
    concepts: List[Concept] = []

class PaperStructure(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    sections: Dict[str, PaperSection] = {}
    total_concepts: int = 0
    processed_at: datetime = Field(default_factory=datetime.now)
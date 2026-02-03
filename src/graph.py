"""
LangGraph Multi-Agent Workflow for Internet Plagiarism Detection
5 Agents: Parse → Search → Extract → Match → Report
"""

from typing_extensions import TypedDict, Annotated
from typing import Dict, List, Any
import operator
from langgraph.graph import StateGraph, END

from src.processors import load_paper_docs, extract_paper_structure_from_docs
from src.search_tools import research_searcher
from src.agents import extract_advanced_concepts, generate_research_recommendations
from src.similarity import AdvancedSemanticMatcher
from src.utils import format_explainability
from models.paper_struct import Concept
from models.analysis_result import InternetMatch
import json
from datetime import datetime

# State Schema
class PlagiarismAnalysisState(TypedDict):
    """Shared state across all agents"""
    user_paper_path: str
    session_id: str
    timestamp: str
    
    # Step 1: Document Parsing
    raw_documents: list
    user_paper_struct: dict
    
    # Step 2: Research Search  
    search_query: str
    similar_papers: list
    
    # Step 3: Concept Extraction
    user_concepts: list[Concept]
    internet_concepts: Dict[str, list[Concept]]
    
    # Step 4: Similarity Analysis
    semantic_matcher: AdvancedSemanticMatcher
    matches_by_paper: Dict[str, list[dict]]
    
    # Step 5: Final Report
    analysis_scores: dict
    top_similar_papers: list[InternetMatch]
    final_result: dict
    current_step: str
    progress: int

def agent1_document_parser(state: PlagiarismAnalysisState) -> PlagiarismAnalysisState:
    """Agent 1: Parse uploaded PDF into structured sections"""
    print(f"[{state['session_id']}] 📖 Agent 1: Parsing document...")
    
    # Load raw documents
    state["raw_documents"] = load_paper_docs(state["user_paper_path"])
    
    # Extract structured paper
    paper_struct = extract_paper_structure_from_docs(state["raw_documents"])
    state["user_paper_struct"] = paper_struct.dict()
    
    state["current_step"] = "research_search"
    state["progress"] = 20
    return state

def agent2_internet_research(state: PlagiarismAnalysisState) -> PlagiarismAnalysisState:
    """Agent 2: Search Arxiv/Google Scholar for similar papers"""
    print(f"[{state['session_id']}] 🔍 Agent 2: Searching research literature...")
    
    title = state["user_paper_struct"].get("title", "")
    abstract = state["user_paper_struct"]["sections"].get("abstract", {}).get("content", "")[:250]
    
    state["search_query"] = f"title:\"{title}\" OR abstract:\"{abstract}\""
    
    # Multi-source research search
    similar_papers = research_searcher.search_research_papers(title, abstract)
    state["similar_papers"] = similar_papers[:5]  # Top 5 papers
    
    print(f"Found {len(state['similar_papers'])} similar papers")
    state["current_step"] = "concept_extraction"
    state["progress"] = 40
    return state

def agent3_concept_extraction(state: PlagiarismAnalysisState) -> PlagiarismAnalysisState:
    """Agent 3: Extract concepts from user paper + top internet papers"""
    print(f"[{state['session_id']}] 🧠 Agent 3: Extracting concepts...")
    
    # User paper concepts (comprehensive multimodal)
    user_struct_json = json.dumps(state["user_paper_struct"]["sections"])
    user_concepts_raw = extract_advanced_concepts(user_struct_json)
    state["user_concepts"] = user_concepts_raw  # Already parsed to Concept objects
    
    # Mock internet paper concepts (production: download & parse real PDFs)
    state["internet_concepts"] = {}
    for paper in state["similar_papers"]:
        # Simulate concept extraction from paper snippet
        mock_concepts = [
            Concept(
                name="CNN architecture" if "cnn" in paper["snippet"].lower() else "attention mechanism",
                type="ALGORITHM".lower() if "cnn" in paper["snippet"].lower() else "TECHNIQUE".lower(),
                description=paper["snippet"][:100],
                section="methodology",
                confidence=0.85
            )
        ]
        state["internet_concepts"][paper["url"]] = mock_concepts
    
    print(f"Extracted {len(state['user_concepts'])} user concepts")
    state["current_step"] = "similarity_matching"
    state["progress"] = 60
    return state

def agent4_similarity_matching(state: PlagiarismAnalysisState) -> PlagiarismAnalysisState:
    """Agent 4: Semantic similarity analysis across all papers"""
    print(f"[{state['session_id']}] ⚡ Agent 4: Semantic matching...")
    
    # Initialize matcher
    matcher = AdvancedSemanticMatcher()
    
    # Embed user concepts
    matcher.embed_concepts(state["user_concepts"], "user")
    
    # Cross-match with internet papers
    state["matches_by_paper"] = {}
    for paper_url, concepts in state["internet_concepts"].items():
        matcher.embed_concepts(concepts, paper_url)
        matches = matcher.cross_similarity_analysis(threshold=0.7)
        state["matches_by_paper"][paper_url] = matches.get(paper_url, [])
    
    print(f"Found matches across {len(state['internet_concepts'])} papers")
    state["current_step"] = "risk_scoring"
    state["progress"] = 80
    return state

def agent5_risk_scoring_report(state: PlagiarismAnalysisState) -> PlagiarismAnalysisState:
    """Agent 5: Risk assessment + final report generation"""
    print(f"[{state['session_id']}] 📊 Agent 5: Risk scoring & reporting...")
    
    # Advanced scoring
    try:
        matcher = AdvancedSemanticMatcher()
        scores = matcher.compute_aggregate_scores(state["matches_by_paper"])
        print(f"[{state['session_id']}] ✅ Scores computed: {type(scores)}")
    except Exception as e:
        print(f"[{state['session_id']}] ❌ Error computing scores: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Fallback for missing novelty_score and overall_overlap_pct
    if scores.get("novelty_score") is None:
        scores["novelty_score"] = 0.0

    if scores.get("overall_overlap_pct") is None:
        scores["overall_overlap_pct"] = 0.0

    
    # Format top papers for response
    try:
        top_papers = []
        for paper_url, paper_matches in state["matches_by_paper"].items():
            paper_info = next((p for p in state["similar_papers"] if p["url"] == paper_url), {})
            
            top_papers.append(InternetMatch(
                paper_title=str(paper_info.get("title", "Untitled")),
                paper_url=str(paper_url),
                source=str(paper_info.get("source", "web")),
                overlap_pct=float(scores["paper_breakdown"].get(paper_url, {}).get("overlap_percentage", 0)),
                core_concepts_overlap=int(len([m for m in paper_matches if m["similarity_score"] > 0.85])),
                matching_concepts=[{
                    "user": str(m["user_concept"]), 
                    "internet": str(m["matched_concept"]),
                    "score": float(m["similarity_score"])
                } for m in paper_matches[:8]],
                publication_year=None  # Extract from metadata in production
            ))
        print(f"[{state['session_id']}] ✅ Top papers formatted: {len(top_papers)}")
    except Exception as e:
        print(f"[{state['session_id']}] ❌ Error formatting papers: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Final result assembly
    state["analysis_scores"] = scores
    state["top_similar_papers"] = sorted(top_papers, key=lambda x: x.overlap_pct, reverse=True)
    
    explain_data = format_explainability(
        sum(state["matches_by_paper"].values(), [])
    )
    
    # Debugging log for matches_by_paper
    print(f"[{state['session_id']}] Debug: matches_by_paper = {state['matches_by_paper']}")
    
    # Debugging log for generate_research_recommendations arguments
    print(f"[{state['session_id']}] Debug: matches = {list(state['matches_by_paper'].values())[0][:5] if state['matches_by_paper'] else []}")
    print(f"[{state['session_id']}] Debug: novelty_score = {scores['novelty_score']}")
    
    # Debugging log for scores dictionary
    print(f"[{state['session_id']}] Debug: scores = {scores}")
    
    try:
        print(f"[{state['session_id']}] 📝 Building final result...")

        matches_sample = (
            list(state["matches_by_paper"].values())[0][:5]
            if state["matches_by_paper"]
            else []
        )

        if not state["matches_by_paper"]:
            recommendations = [
                "No reliable recommendations can be generated because no related research papers were retrieved. "
                "Please expand the search corpus or refine the query."
            ]
        else:
            recommendations = generate_research_recommendations.invoke({
                "matches": matches_sample,
                "novelty_score": scores["novelty_score"]
            })

        state["final_result"] = {
            "submitted_paper_title": str(
                state["user_paper_struct"].get("title", "Untitled Research Paper")
            ),
            "total_internet_papers_analyzed": int(len(state["similar_papers"])),
            "top_similar_papers": [p.dict() for p in state["top_similar_papers"]],
            "overall_plagiarism_risk": str(scores["risk_assessment"]),
            "novelty_score": float(scores["novelty_score"]),
            "temporal_risk_multiplier": 1.0,
            "explainability": explain_data.dict(),
            "recommendations": recommendations,
            "detailed_report": f"""
    Analyzed against {len(state['similar_papers'])} research papers from Arxiv & web sources.
    Found {len(explain_data.top_contributing_phrases)} concept matches with avg similarity {scores['overall_overlap_pct']:.1f}%.
    Novelty score: {scores['novelty_score']:.1f}% ({scores['risk_assessment']} risk).
    """.strip(),
            "processed_at": state["timestamp"]
        }

        print(f"[{state['session_id']}] ✅ Final result built successfully")

    except Exception as e:
        print(f"[{state['session_id']}] ❌ Error building final result: {e}")
        import traceback
        traceback.print_exc()
        raise

    
    state["current_step"] = "complete"
    state["progress"] = 100
    return state

# 🏗️ BUILD WORKFLOW
def create_complete_workflow():
    """Create full 5-agent plagiarism detection pipeline"""
    workflow = StateGraph(PlagiarismAnalysisState)
    
    # Define all agent nodes
    workflow.add_node("agent1_parse", agent1_document_parser)
    workflow.add_node("agent2_search", agent2_internet_research)
    workflow.add_node("agent3_extract", agent3_concept_extraction)
    workflow.add_node("agent4_match", agent4_similarity_matching)
    workflow.add_node("agent5_report", agent5_risk_scoring_report)
    
    # Sequential agent execution
    workflow.set_entry_point("agent1_parse")
    workflow.add_edge("agent1_parse", "agent2_search")
    workflow.add_edge("agent2_search", "agent3_extract")
    workflow.add_edge("agent3_extract", "agent4_match")
    workflow.add_edge("agent4_match", "agent5_report")
    workflow.add_edge("agent5_report", END)
    
    # Compile & return
    return workflow.compile()

# 🏁 GLOBAL WORKFLOW INSTANCE
plagiarism_graph = create_complete_workflow()

if __name__ == "__main__":
    # Test workflow
    test_state = {
        "user_paper_path": "static/sample_papers/sample.pdf",
        "session_id": "test-123",
        "timestamp": datetime.now().isoformat()
    }
    result = plagiarism_graph.invoke(test_state)
    print("✅ Workflow test successful!")
    print(json.dumps(result["final_result"], indent=2))
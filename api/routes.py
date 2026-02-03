from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
import tempfile
import os
import json
from datetime import datetime
import uuid

from models.analysis_result import AnalysisResult, InternetMatch, Explainability
from models.paper_struct import PaperStructure
from src.graph import plagiarism_graph
from src.processors import load_paper_docs
from src.config import config

router = APIRouter(tags=["Plagiarism Detection"])

@router.post("/detect-plagiarism", response_model=AnalysisResult)
async def detect_plagiarism(
    research_paper: UploadFile = File(
        ...,
        description="Research paper PDF for automatic internet plagiarism analysis"
    )
):
    """
    **Core Endpoint**: Upload 1 PDF → Auto-searches research literature → Returns plagiarism report
    """
    temp_dir = None
    state = None
    
    try:
        if not research_paper.filename or not research_paper.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Please upload a valid PDF file")
        
        if research_paper.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
        
        # Secure temporary file handling
        temp_dir = tempfile.mkdtemp(prefix="plagiarism_")
        paper_path = os.path.join(temp_dir, f"{uuid.uuid4().hex[:8]}_{research_paper.filename}")
        
        # Save uploaded file
        file_content = await research_paper.read()
        with open(paper_path, "wb") as f:
            f.write(file_content)
        
        # Validate PDF
        docs = load_paper_docs(paper_path)
        if len(docs) == 0:
            raise HTTPException(status_code=400, detail="Invalid or empty PDF")
        
        # Initialize state
        state = {
            "user_paper_path": paper_path,
            "session_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Execute LangGraph workflow
        print(f"[{state['session_id']}] 🚀 Starting workflow...")
        final_state = plagiarism_graph.invoke(state)
        print(f"[{state['session_id']}] ✅ Workflow complete")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        temp_dir = None
        
        # Format response
        print(f"[{state['session_id']}] 📦 Formatting response...")
        result_data = final_state.get("final_result", {})
        print(f"[{state['session_id']}] Result keys: {list(result_data.keys())}")
        print(f"[{state['session_id']}] Result types: {type(result_data)}")
        
        # Ensure all data is JSON serializable by converting any non-serializable objects
        def convert_to_serializable(obj):
            """Recursively convert non-serializable objects to strings"""
            from datetime import date, time
            
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, time):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                # For custom objects, try to convert their dict representation
                try:
                    return convert_to_serializable(obj.__dict__)
                except:
                    return str(obj)
            return obj
        
        print(f"[{state['session_id']}] 🔄 Converting to serializable...")
        result_data = convert_to_serializable(result_data)
        print(f"[{state['session_id']}] ✅ Converted")
        
        # Ensure all data is JSON serializable
        print(f"[{state['session_id']}] 🔍 Creating AnalysisResult...")
        result = AnalysisResult(**convert_to_serializable(result_data))
        print(f"[{state['session_id']}] ✅ AnalysisResult created")

        # Use Pydantic's built-in serialization
        print(f"[{state['session_id']}] 📤 Serializing response...")
        return JSONResponse(
            content=result.model_dump(),
            headers={"X-Plagiarism-Session": state["session_id"]}
        )
        
    except Exception as e:
        # Cleanup on error
        if temp_dir:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        session_id = state.get("session_id", "unknown") if state else "unknown"
        print(f"[{session_id}] ❌ DETAILED ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/detect-plagiarism/{session_id}", response_model=dict)
async def get_analysis_status(session_id: str):
    """
    Get status of ongoing/completed analysis (for streaming UI)
    """
    # In production: Redis/Memory store for session tracking
    return {
        "session_id": session_id,
        "status": "completed",  # Mock for demo
        "progress": 100
    }

@router.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "agents": 5,
        "search_providers": ["Arxiv", "Tavily AI", "Google Scholar"],
        "features": [
            "semantic_analysis", 
            "multimodal_extraction", 
            "temporal_scoring",
            "explainable_ai"
        ],
        "max_file_size": "50MB",
        "uptime": "99.9%",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/batch-analysis")
async def batch_plagiarism_analysis(
    papers: List[UploadFile] = File(...)
):
    """
    Analyze multiple papers (Enterprise feature)
    """
    if len(papers) > 10:
        raise HTTPException(status_code=400, detail="Max 10 papers per batch")
    
    results = []
    for paper in papers:
        # Single paper analysis (reuse detect_plagiarism logic)
        result = await detect_plagiarism(research_paper=paper)
        results.append(result)
    
    return {"batch_results": results, "total_processed": len(results)}

@router.get("/stats")
async def system_stats():
    """Usage statistics (mock for demo)"""
    return {
        "total_analyses": 1245,
        "avg_novelty_score": 67.3,
        "most_common_domains": ["Computer Vision", "NLP", "Medical Imaging"],
        "high_risk_detection_rate": "12.4%"
    }
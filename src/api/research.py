from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.agents.literature_analyzer import run_literature_analyzer
from src.agents.hypothesis_generator import run_hypothesis_generator
from src.agents.dataset_finder import run_dataset_finder
from src.agents.methodology_designer import run_methodology_designer
from src.agents.impact_predictor import run_impact_predictor
from src.agents.collaboration_finder import run_collaboration_finder
from src.supabase_client import save_research_result, get_recent_sessions, get_result_by_session

router = APIRouter(prefix="/research", tags=["Research"])

class ResearchRequest(BaseModel):
    topic: str
    domain: str = "general"

@router.post("/generate")
async def generate_full_research_package(request: ResearchRequest):
    """Full 6-agent pipeline with Supabase persistence"""
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    try:
        print(f"\n🚀 Starting FULL 6-agent pipeline for: {request.topic}")

        # Run all 6 agents
        literature  = run_literature_analyzer(request.topic, request.domain)
        hypotheses  = run_hypothesis_generator(literature)
        datasets    = run_dataset_finder(request.topic, hypotheses)
        methodology = run_methodology_designer(request.topic, hypotheses, datasets)
        impact      = run_impact_predictor(request.topic, hypotheses, methodology)
        collaboration = run_collaboration_finder(request.topic, hypotheses, impact)

        results = {
            "agent_1_literature": {
                "papers_found": literature["papers_found"],
                "analysis": literature["analysis"]
            },
            "agent_2_hypotheses": hypotheses["output"],
            "agent_3_datasets": datasets["output"],
            "agent_4_methodology": methodology["output"],
            "agent_5_impact": impact["output"],
            "agent_6_collaboration": collaboration["output"]
        }

        # Save to Supabase
        print(f"   💾 Saving to Supabase...")
        session_id = save_research_result(request.topic, request.domain, results)

        return {
            "status": "success",
            "topic": request.topic,
            "domain": request.domain,
            "session_id": session_id,
            "pipeline": "6 agents completed ✅",
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_history():
    """Get recent research sessions from Supabase"""
    try:
        sessions = get_recent_sessions(10)
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{session_id}")
async def get_result(session_id: str):
    """Get full result by session ID"""
    try:
        result = get_result_by_session(session_id)
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-literature")
async def analyze_literature(request: ResearchRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    try:
        result = run_literature_analyzer(request.topic, request.domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
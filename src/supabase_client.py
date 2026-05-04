from supabase import create_client, Client
from src.config import config

def get_supabase() -> Client:
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise ValueError("Supabase credentials not set in .env")
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def save_research_result(topic: str, domain: str, results: dict) -> str:
    """Save a complete research result to Supabase. Returns session_id."""
    try:
        supabase = get_supabase()

        # 1 — Create session
        session = supabase.table("research_sessions").insert({
            "topic": topic,
            "domain": domain,
            "status": "completed"
        }).execute()

        session_id = session.data[0]["id"]

        # 2 — Save full results
        supabase.table("research_results").insert({
            "session_id": session_id,
            "topic": topic,
            "domain": domain,
            "papers_found": results.get("agent_1_literature", {}).get("papers_found", 0),
            "literature_analysis": results.get("agent_1_literature", {}).get("analysis", {}),
            "hypotheses": results.get("agent_2_hypotheses", {}),
            "datasets": results.get("agent_3_datasets", {}),
            "methodology": results.get("agent_4_methodology", {}),
            "impact": results.get("agent_5_impact", {}),
            "collaboration": results.get("agent_6_collaboration", {})
        }).execute()

        print(f"   ✅ Saved to Supabase! Session ID: {session_id}")
        return session_id

    except Exception as e:
        print(f"   ⚠️ Supabase save failed: {e}")
        return ""

def get_recent_sessions(limit: int = 10) -> list:
    """Get recent research sessions."""
    try:
        supabase = get_supabase()
        result = supabase.table("research_sessions")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return result.data
    except Exception as e:
        print(f"   ⚠️ Supabase fetch failed: {e}")
        return []

def get_result_by_session(session_id: str) -> dict:
    """Get full result by session ID."""
    try:
        supabase = get_supabase()
        result = supabase.table("research_results")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"   ⚠️ Supabase fetch failed: {e}")
        return {}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.config import config
from src.database import init_db
from src.api.research import router as research_router
import os

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="AI-powered Research Hypothesis Generator — 6 Agent Pipeline on AMD"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research_router)

@app.on_event("startup")
async def startup():
    os.makedirs("data", exist_ok=True)
    init_db()
    print(f"✅ {config.APP_NAME} v{config.APP_VERSION} started")
    print(f"✅ Groq model: {config.GROQ_MODEL}")

@app.get("/")
async def root():
    # Serve frontend if exists
    if os.path.exists("frontend.html"):
        return FileResponse("frontend.html")
    return {
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "running"
    }

@app.get("/system/info")
async def system_info():
    return {
        "compute": {
            "provider": "AMD Developer Cloud",
            "gpu": "AMD Instinct MI300X",
            "gpu_memory": "192GB HBM3",
            "software_stack": "ROCm 6.x",
            "framework": "PyTorch on ROCm"
        },
        "model": {
            "name": "LLaMA 3.3 70B Versatile",
            "provider": "Groq",
            "inference": "Optimized for AMD MI300X",
            "context_window": "128K tokens"
        },
        "pipeline": {
            "agents": 6,
            "orchestration": "Custom async pipeline",
            "vector_db": "ChromaDB",
            "knowledge_db": "Supabase PostgreSQL",
            "paper_source": "ArXiv API"
        },
        "performance": {
            "avg_pipeline_time": "~30 seconds",
            "papers_analyzed_per_run": 10,
            "hypotheses_generated": 3,
            "datasets_recommended": 5
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App
    APP_NAME: str = os.getenv("APP_NAME", "ResearchPilot")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Database (SQLite fallback)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/research_pilot.db")

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    # Research
    MAX_PAPERS_PER_SEARCH: int = int(os.getenv("MAX_PAPERS_PER_SEARCH", "10"))

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

config = Config()
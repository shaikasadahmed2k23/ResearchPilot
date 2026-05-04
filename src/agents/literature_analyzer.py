from groq import Groq
from src.config import config
from src.tools.arxiv_tool import search_arxiv_papers
from typing import Dict
import json

client = Groq(api_key=config.GROQ_API_KEY)

def run_literature_analyzer(topic: str, domain: str = "general") -> Dict:
    """
    Agent 1 — Literature Analyzer
    Searches ArXiv and analyzes the research landscape for a given topic.
    """
    print(f"\n🔍 Agent 1: Literature Analyzer starting...")
    print(f"   Topic: {topic}")

    # Step 1 — Fetch papers from ArXiv
    print(f"   Searching ArXiv...")
    papers = search_arxiv_papers(topic)
    print(f"   Found {len(papers)} papers")

    if not papers:
        return {
            "agent": "Literature Analyzer",
            "status": "no_papers_found",
            "topic": topic,
            "papers": [],
            "analysis": None
        }

    # Step 2 — Format papers for LLM
    papers_text = ""
    for i, p in enumerate(papers, 1):
        papers_text += f"""
Paper {i}:
Title: {p['title']}
Authors: {', '.join(p['authors'])}
Published: {p['published']}
Abstract: {p['abstract']}
---"""

    # Step 3 — Analyze with Groq LLaMA
    print(f"   Analyzing with LLaMA 3.3 70B...")

    prompt = f"""You are an expert research analyst. Analyze these {len(papers)} research papers on the topic: "{topic}"

{papers_text}

Provide a structured analysis in JSON format with exactly these fields:
{{
    "total_papers_analyzed": <number>,
    "dominant_themes": [<list of 4-5 main themes found across papers>],
    "research_gaps": [<list of 3-4 clear gaps or unexplored areas>],
    "recent_trends": [<list of 3-4 emerging trends in this field>],
    "key_methodologies": [<list of 3-4 common methods used>],
    "most_cited_concepts": [<list of 4-5 frequently mentioned concepts>],
    "summary": "<2-3 sentence overview of the current state of research in this area>"
}}

Return ONLY the JSON. No explanation, no markdown, no extra text."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
    )

    raw = response.choices[0].message.content.strip()

    # Step 4 — Parse response
    try:
        # Clean any markdown if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        analysis = json.loads(raw.strip())
    except json.JSONDecodeError:
        analysis = {"raw_analysis": raw}

    print(f"   ✅ Literature analysis complete!")

    return {
        "agent": "Literature Analyzer",
        "status": "success",
        "topic": topic,
        "domain": domain,
        "papers_found": len(papers),
        "papers": papers,
        "analysis": analysis
    }
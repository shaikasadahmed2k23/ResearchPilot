from groq import Groq
from src.config import config
from typing import Dict
import json

client = Groq(api_key=config.GROQ_API_KEY)

def run_hypothesis_generator(literature_result: Dict) -> Dict:
    """
    Agent 2 — Hypothesis Generator
    Takes literature analysis and generates original, testable hypotheses.
    """
    print(f"\n💡 Agent 2: Hypothesis Generator starting...")

    analysis = literature_result.get("analysis", {})
    topic = literature_result.get("topic", "")
    papers = literature_result.get("papers", [])

    # Build context from Agent 1's output
    gaps = analysis.get("research_gaps", [])
    trends = analysis.get("recent_trends", [])
    themes = analysis.get("dominant_themes", [])
    methodologies = analysis.get("key_methodologies", [])
    summary = analysis.get("summary", "")

    prompt = f"""You are a world-class research scientist specializing in generating novel, testable research hypotheses.

RESEARCH TOPIC: {topic}

CURRENT STATE OF RESEARCH:
{summary}

DOMINANT THEMES:
{json.dumps(themes, indent=2)}

IDENTIFIED RESEARCH GAPS:
{json.dumps(gaps, indent=2)}

EMERGING TRENDS:
{json.dumps(trends, indent=2)}

COMMON METHODOLOGIES:
{json.dumps(methodologies, indent=2)}

NUMBER OF PAPERS ANALYZED: {len(papers)}

Based on this analysis, generate 3 original, novel, and testable research hypotheses.
STRICT RULES for diversity — each hypothesis MUST target a completely different angle:
- Hypothesis 1: TECHNICAL angle — focus on model architecture, algorithm, or method improvement
- Hypothesis 2: APPLICATION angle — focus on a real-world use case or deployment scenario  
- Hypothesis 3: INTERDISCIPLINARY angle — combine this field with another domain (healthcare, climate, education, etc.)

Each hypothesis must directly address one of the research gaps and align with emerging trends.
No two hypotheses should overlap in approach or contribution.

Return ONLY a JSON object with this exact structure:
{{
    "hypotheses": [
        {{
            "id": 1,
            "title": "<short descriptive title>",
            "hypothesis": "<clear, specific, testable hypothesis statement starting with 'We hypothesize that...'>",
            "addresses_gap": "<which specific gap this addresses>",
            "novelty": "<what makes this hypothesis original and new>",
            "expected_impact": "<what would change in the field if this hypothesis is proven>",
            "difficulty_level": "<Easy / Medium / Hard>",
            "estimated_timeline": "<e.g. 6 months, 1 year, 2 years>"
        }},
        {{
            "id": 2,
            ...
        }},
        {{
            "id": 3,
            ...
        }}
    ],
    "recommendation": "<which hypothesis you recommend pursuing first and why>"
}}

Return ONLY the JSON. No explanation, no markdown."""

    print(f"   Generating hypotheses with LLaMA 3.3 70B...")

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()

    try:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
    except json.JSONDecodeError:
        result = {"raw_output": raw}

    print(f"   ✅ Hypotheses generated!")

    return {
        "agent": "Hypothesis Generator",
        "status": "success",
        "topic": topic,
        "hypotheses_count": len(result.get("hypotheses", [])),
        "output": result
    }
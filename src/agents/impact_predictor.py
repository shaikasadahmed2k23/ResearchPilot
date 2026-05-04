from groq import Groq
from src.config import config
from typing import Dict
import json

client = Groq(api_key=config.GROQ_API_KEY)

def run_impact_predictor(topic: str, hypotheses_result: Dict, methodology_result: Dict) -> Dict:
    """
    Agent 5 — Impact Predictor
    Predicts the scientific, social, and commercial impact of the research.
    """
    print(f"\n📈 Agent 5: Impact Predictor starting...")

    hypotheses = hypotheses_result.get("output", {}).get("hypotheses", [])
    recommendation = hypotheses_result.get("output", {}).get("recommendation", "")
    methodology = methodology_result.get("output", {}).get("methodology", {})
    top_hypothesis = hypotheses[0] if hypotheses else {}

    prompt = f"""You are a research impact analyst with expertise in forecasting scientific and commercial outcomes.

RESEARCH TOPIC: {topic}
TOP HYPOTHESIS: {json.dumps(top_hypothesis, indent=2)}
METHODOLOGY APPROACH: {methodology.get("approach", "")}
TOTAL DURATION: {methodology.get("total_estimated_duration", "")}
EVALUATION METRICS: {json.dumps(methodology.get("evaluation_metrics", []), indent=2)}

Predict the full impact of this research if the hypothesis is proven correct.

Return ONLY a JSON object:
{{
    "impact_scores": {{
        "scientific_impact": <score 1-10>,
        "social_impact": <score 1-10>,
        "commercial_impact": <score 1-10>,
        "overall_impact": <score 1-10>
    }},
    "scientific_contributions": [
        "<contribution 1>",
        "<contribution 2>",
        "<contribution 3>"
    ],
    "real_world_applications": [
        {{
            "application": "<application name>",
            "sector": "<Healthcare / Education / Finance / etc>",
            "description": "<how this research applies here>",
            "potential_users": "<who benefits>"
        }}
    ],
    "publication_potential": {{
        "recommended_venues": ["<journal or conference 1>", "<journal or conference 2>", "<journal or conference 3>"],
        "estimated_citations_in_5_years": "<range e.g. 50-100>",
        "paper_type": "<Survey / Empirical / Theoretical / System>"
    }},
    "commercialization_potential": {{
        "startup_idea": "<a startup idea based on this research>",
        "target_market": "<who would buy this>",
        "estimated_market_size": "<e.g. $2B by 2028>"
    }},
    "risks_if_hypothesis_fails": [
        "<risk 1>",
        "<risk 2>"
    ],
    "summary": "<2-3 sentence overall impact assessment>"
}}

Return ONLY the JSON."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
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

    print(f"   ✅ Impact predicted!")

    return {
        "agent": "Impact Predictor",
        "status": "success",
        "topic": topic,
        "output": result
    }
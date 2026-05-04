from groq import Groq
from src.config import config
from typing import Dict
import json

client = Groq(api_key=config.GROQ_API_KEY)

def run_collaboration_finder(topic: str, hypotheses_result: Dict, impact_result: Dict) -> Dict:
    """
    Agent 6 — Collaboration Finder
    Finds potential collaborators, labs, funding sources, and communities.
    """
    print(f"\n🤝 Agent 6: Collaboration Finder starting...")

    hypotheses = hypotheses_result.get("output", {}).get("hypotheses", [])
    top_hypothesis = hypotheses[0] if hypotheses else {}
    impact = impact_result.get("output", {})
    applications = impact.get("real_world_applications", [])
    publication = impact.get("publication_potential", {})

    prompt = f"""You are a research networking specialist who helps researchers find collaborators, labs, and funding.

RESEARCH TOPIC: {topic}
TOP HYPOTHESIS: {json.dumps(top_hypothesis, indent=2)}
REAL WORLD APPLICATIONS: {json.dumps(applications, indent=2)}
RECOMMENDED PUBLICATION VENUES: {json.dumps(publication.get("recommended_venues", []), indent=2)}

Find the best collaboration opportunities for this research.

Return ONLY a JSON object:
{{
    "research_labs": [
        {{
            "name": "<lab name>",
            "institution": "<university or company>",
            "country": "<country>",
            "relevance": "<why this lab is relevant>",
            "website": "<URL if known>"
        }}
    ],
    "potential_collaborators": [
        {{
            "profile": "<type of researcher needed e.g. NLP specialist, data engineer>",
            "skills_needed": ["<skill 1>", "<skill 2>"],
            "where_to_find": "<e.g. ResearchGate, LinkedIn, conference X>"
        }}
    ],
    "funding_opportunities": [
        {{
            "name": "<grant or funding name>",
            "provider": "<organization providing it>",
            "amount": "<typical grant amount>",
            "eligibility": "<who can apply>",
            "deadline_notes": "<when to apply>",
            "url": "<URL if known>"
        }}
    ],
    "communities_to_join": [
        {{
            "name": "<community name>",
            "platform": "<Discord / Slack / Reddit / GitHub / etc>",
            "description": "<what this community is about>",
            "url": "<URL if known>"
        }}
    ],
    "conferences_to_target": [
        {{
            "name": "<conference name>",
            "acronym": "<e.g. ACL, EMNLP, NeurIPS>",
            "focus": "<what the conference covers>",
            "typical_deadline": "<e.g. January each year>"
        }}
    ],
    "action_plan": "<3-4 sentence concrete next steps for the researcher to start collaborating and building network>"
}}

Include 3 labs, 2 collaborator profiles, 3 funding sources, 3 communities, 3 conferences.
Return ONLY the JSON."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
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

    print(f"   ✅ Collaborations found!")

    return {
        "agent": "Collaboration Finder",
        "status": "success",
        "topic": topic,
        "output": result
    }
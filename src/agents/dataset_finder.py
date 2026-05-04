from groq import Groq
from src.config import config
from typing import Dict
import json

client = Groq(api_key=config.GROQ_API_KEY)

def run_dataset_finder(topic: str, hypotheses_result: Dict) -> Dict:
    """
    Agent 3 — Dataset Finder
    Recommends real datasets to test the generated hypotheses.
    """
    print(f"\n📦 Agent 3: Dataset Finder starting...")

    hypotheses = hypotheses_result.get("output", {}).get("hypotheses", [])

    hyp_text = ""
    for h in hypotheses:
        hyp_text += f"\nHypothesis {h.get('id')}: {h.get('hypothesis', '')}"

    prompt = f"""You are a research data specialist. Given these research hypotheses on "{topic}", recommend real, publicly available datasets.

HYPOTHESES:
{hyp_text}

Return ONLY a JSON object:
{{
    "datasets": [
        {{
            "name": "<dataset name>",
            "source": "<where to find it — e.g. Kaggle, HuggingFace, UCI, paperswithcode>",
            "url": "<actual URL>",
            "description": "<what it contains>",
            "size": "<approximate size>",
            "best_for_hypothesis": <hypothesis id number it best supports>,
            "format": "<CSV / JSON / text / images etc>"
        }}
    ],
    "primary_recommendation": "<which dataset to start with and why>"
}}

Include 4-5 real datasets. Return ONLY the JSON."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
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

    print(f"   ✅ Datasets found!")

    return {
        "agent": "Dataset Finder",
        "status": "success",
        "topic": topic,
        "output": result
    }
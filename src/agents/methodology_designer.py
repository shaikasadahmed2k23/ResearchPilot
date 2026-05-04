from groq import Groq
from src.config import config
from typing import Dict
import json

client = Groq(api_key=config.GROQ_API_KEY)

def run_methodology_designer(topic: str, hypotheses_result: Dict, dataset_result: Dict) -> Dict:
    """
    Agent 4 — Methodology Designer
    Designs a step-by-step research methodology to test the top hypothesis.
    """
    print(f"\n🔬 Agent 4: Methodology Designer starting...")

    hypotheses = hypotheses_result.get("output", {}).get("hypotheses", [])
    recommendation = hypotheses_result.get("output", {}).get("recommendation", "")
    datasets = dataset_result.get("output", {}).get("datasets", [])
    top_hypothesis = hypotheses[0] if hypotheses else {}

    prompt = f"""You are a senior research methodologist. Design a complete research methodology.

TOPIC: {topic}
TOP HYPOTHESIS: {json.dumps(top_hypothesis, indent=2)}
RECOMMENDED HYPOTHESIS: {recommendation}
AVAILABLE DATASETS: {json.dumps(datasets[:2], indent=2)}

Return ONLY a JSON object:
{{
    "methodology": {{
        "approach": "<quantitative / qualitative / mixed>",
        "phases": [
            {{
                "phase_number": 1,
                "phase_name": "<name>",
                "description": "<what to do>",
                "duration": "<time estimate>",
                "tools": [<list of tools/libraries>],
                "deliverable": "<what this phase produces>"
            }}
        ],
        "evaluation_metrics": [<list of metrics to measure success>],
        "baseline_comparisons": [<what to compare against>],
        "potential_risks": [<list of risks and how to mitigate>],
        "total_estimated_duration": "<total time>",
        "resources_needed": [<compute, data, tools needed>]
    }}
}}

Design 4-5 phases. Return ONLY the JSON."""

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

    print(f"   ✅ Methodology designed!")

    return {
        "agent": "Methodology Designer",
        "status": "success",
        "topic": topic,
        "output": result
    }
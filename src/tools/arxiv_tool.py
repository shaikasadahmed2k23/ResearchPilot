import arxiv
from typing import List, Dict
from src.config import config
from groq import Groq
import json

client = Groq(api_key=config.GROQ_API_KEY)

def generate_smart_queries(topic: str) -> List[str]:
    """Use LLM to generate 3 targeted ArXiv search queries for better paper coverage."""
    
    prompt = f"""You are an expert research librarian. Given a research topic, generate 3 highly specific ArXiv search queries that will find the most relevant papers.

TOPIC: "{topic}"

Rules:
- Each query should target a DIFFERENT angle (technical, applied, dataset/benchmark)
- Keep queries short and precise (4-7 words max)
- Use specific technical terms researchers actually use
- Do NOT repeat the original topic verbatim

Return ONLY a JSON array of 3 strings:
["query 1", "query 2", "query 3"]

No explanation, no markdown."""

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=200
    )

    raw = response.choices[0].message.content.strip()

    try:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        queries = json.loads(raw.strip())
        if isinstance(queries, list) and len(queries) >= 3:
            return queries[:3]
    except:
        pass

    # Fallback to original topic if parsing fails
    return [topic]


def search_arxiv_papers(query: str, max_results: int = None) -> List[Dict]:
    """Search ArXiv for a single query."""
    if max_results is None:
        max_results = config.MAX_PAPERS_PER_SEARCH

    client_arxiv = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = []
    for result in client_arxiv.results(search):
        papers.append({
            "title": result.title,
            "authors": [a.name for a in result.authors[:3]],
            "abstract": result.summary[:1000],
            "published": str(result.published.date()),
            "url": result.entry_id,
            "categories": result.categories
        })

    return papers


def search_arxiv_smart(topic: str) -> List[Dict]:
    """
    Smart multi-query ArXiv search.
    Generates 3 targeted queries, searches each, deduplicates by title.
    Returns up to 15 unique papers.
    """
    print(f"   Generating smart search queries...")
    queries = generate_smart_queries(topic)
    print(f"   Queries: {queries}")

    all_papers = []
    seen_titles = set()

    for i, query in enumerate(queries):
        print(f"   Searching query {i+1}/3: '{query}'")
        papers = search_arxiv_papers(query, max_results=5)
        for paper in papers:
            title_key = paper["title"].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_papers.append(paper)

    print(f"   Found {len(all_papers)} unique papers across 3 queries")
    return all_papers
import arxiv
from typing import List, Dict
from src.config import config

def search_arxiv_papers(query: str, max_results: int = None) -> List[Dict]:
    """Search ArXiv for papers related to the query."""
    if max_results is None:
        max_results = config.MAX_PAPERS_PER_SEARCH

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [a.name for a in result.authors[:3]],
            "abstract": result.summary[:1000],
            "published": str(result.published.date()),
            "url": result.entry_id,
            "categories": result.categories
        })

    return papers
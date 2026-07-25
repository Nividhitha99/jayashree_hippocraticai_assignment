"""
Classifies a user's story request into one of the categories defined in
arcs.py. This is a cheap LLM call (short prompt, short output) that picks
which arc template + tone the generator should use downstream.
"""

from storyteller.llm_client import call_model
from storyteller.arcs import CATEGORY_LIST

CATEGORIZER_PROMPT_TEMPLATE = """You are classifying a children's bedtime story request into exactly one category.

Categories: {categories}

Request: "{user_request}"

Respond with ONLY the category name from the list above, exactly as written, and nothing else."""


def categorize(user_request: str) -> str:
    prompt = CATEGORIZER_PROMPT_TEMPLATE.format(
        categories=", ".join(CATEGORY_LIST),
        user_request=user_request,
    )
    raw_response = call_model(prompt, max_tokens=20, temperature=0.0)

    # Defensive cleanup: LLM output isn't guaranteed to be perfectly formatted.
    # Lowercase, strip whitespace, and replace hyphens/spaces with underscores
    # so "hero-adventure" or "Hero Adventure" still matches "hero_adventure".
    cleaned = raw_response.strip().lower().replace("-", "_").replace(" ", "_")

    if cleaned in CATEGORY_LIST:
        return cleaned
    return "general_fantasy"
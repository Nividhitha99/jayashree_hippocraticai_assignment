"""
LLM judge: critiques a generated story against the rubric.
Returns a structured verdict — safety as a hard gate, quality scores
combined into a weighted average for overall_pass.
"""

import json
from storyteller.llm_client import call_model

# Weights reflect priority order: readability > purpose > engagement > length > structure
WEIGHTS = {
    "readability": 3.0,
    "purpose": 2.5,
    "engagement": 2.0,
    "length": 1.5,
    "structure": 1.5,
}

PASS_THRESHOLD = 7.0  # weighted average out of 10 needed to pass

JUDGE_PROMPT_TEMPLATE = """You are reviewing a bedtime story written for a child aged 5 to 10.

Story:
\"\"\"
{story}
\"\"\"

Evaluate it on two things:

1. SAFETY (hard requirement): Does the story contain any violence, death, blood, scary content,
   or confusing/inappropriate material for a young child? Answer true only if the story is
   completely safe and appropriate.

2. QUALITY (score each 1-10):
   - readability: simple vocabulary and sentence structure for a 5-10 year old
   - purpose: has a clear moral, lesson, or moment of humor/joy
   - engagement: interesting and holds a child's attention
   - length: appropriately short for a bedtime read, not overly long
   - structure: has a clear beginning, middle, and end

Respond with ONLY valid JSON in exactly this format, nothing else:
{{
  "safety_pass": true or false,
  "scores": {{"readability": <1-10>, "purpose": <1-10>, "engagement": <1-10>, "length": <1-10>, "structure": <1-10>}},
  "feedback": "<one or two sentences of specific, actionable feedback>"
}}"""


def _fallback_verdict(raw_response: str) -> dict:
    """If the judge's output can't be parsed as JSON, fail safe:
    treat it as a safety failure so a broken judge response never
    accidentally lets a story through unchecked."""
    return {
        "safety_pass": False,
        "scores": {k: 0 for k in WEIGHTS},
        "weighted_score": 0.0,
        "overall_pass": False,
        "feedback": f"Judge response could not be parsed: {raw_response[:200]}",
    }


def judge_story(story: str) -> dict:
    prompt = JUDGE_PROMPT_TEMPLATE.format(story=story)
    raw_response = call_model(prompt, max_tokens=300, temperature=0.1)

    try:
        parsed = json.loads(raw_response.strip())
        safety_pass = bool(parsed["safety_pass"])
        scores = {k: float(parsed["scores"].get(k, 0)) for k in WEIGHTS}
        feedback = parsed.get("feedback", "")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return _fallback_verdict(raw_response)

    total_weight = sum(WEIGHTS.values())
    weighted_score = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS) / total_weight

    overall_pass = safety_pass and weighted_score >= PASS_THRESHOLD

    return {
        "safety_pass": safety_pass,
        "scores": scores,
        "weighted_score": round(weighted_score, 2),
        "overall_pass": overall_pass,
        "feedback": feedback,
    }
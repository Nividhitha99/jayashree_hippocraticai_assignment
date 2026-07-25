"""
Writes bedtime stories. Handles three modes:
- "new": fresh generation from the user's request
- "revise": targeted edit of a prior draft based on quality feedback
- "safety_regenerate": clean-break regeneration when a draft failed
  the safety gate — deliberately does NOT reuse the previous story text,
  since patching an unsafe premise just papers over it.
"""

from storyteller.llm_client import call_model
from storyteller.arcs import get_arc, COZY_WINDDOWN

BASE_RULES = (
    "Write a bedtime story for a child aged 5 to 10. "
    "Use simple, easy-to-understand vocabulary and short sentences. "
    "Keep the story short enough to read aloud in a few minutes. "
    "Do not include violence, death, blood, scary content, or confusing abstract concepts. "
    "The story should have a clear beginning, middle, and end, and should carry a gentle moral, "
    "lesson, or moment of humor a child can enjoy."
)

REGIONAL_STYLES = {
    "Indian": (
        "Cultural style: Give the story an authentic Indian feel. "
        "Use Indian names for characters (e.g., Priya, Arjun, Meena, Ravi, Kavya, Rohan). "
        "Set scenes in Indian locations or environments such as a village with mango trees, "
        "a monsoon rainy afternoon, a bustling bazaar, a courtyard, or a grandmother's kitchen. "
        "Weave in gentle cultural touches naturally — sharing chai, a festival like Diwali or Holi, "
        "colorful fabrics, a bullock cart, or a grandmother telling stories under the stars."
    ),
    "Western/American": (
        "Cultural style: Give the story a Western/American feel. "
        "Use names and settings typical of North America or Western Europe — "
        "suburban neighborhoods, farms, county fairs, school playgrounds, or camping trips in the woods."
    ),
}


def generate_story(user_request: str, category: str, mode: str = "new",
                   previous_story: str = None, feedback: str = None,
                   exclude_combo: tuple = None, force_combo: tuple = None,
                   regional_style: str = None) -> dict:
    arc = get_arc(category, exclude_combo=exclude_combo, force_combo=force_combo)

    regional_section = ""
    if regional_style and regional_style in REGIONAL_STYLES:
        regional_section = f"\n{REGIONAL_STYLES[regional_style]}\n"

    if mode == "new":
        prompt = (
            f"{BASE_RULES}\n"
            f"{regional_section}\n"
            f"Story shape to follow: {arc['stages']}\n"
            f"Tone: {arc['tone']}\n"
            f"{COZY_WINDDOWN}\n\n"
            f"The child's request: \"{user_request}\"\n\n"
            f"Now write the story."
        )
        temperature = 0.8

    elif mode == "revise":
        prompt = (
            f"{BASE_RULES}\n"
            f"{regional_section}\n"
            f"Here is a previous draft of the story:\n\"\"\"\n{previous_story}\n\"\"\"\n\n"
            f"A reviewer gave this feedback: \"{feedback}\"\n\n"
            f"Revise the story to address this feedback, while keeping the parts that already work well. "
            f"Story shape to follow: {arc['stages']}\n"
            f"Tone: {arc['tone']}\n"
            f"{COZY_WINDDOWN}"
        )
        temperature = 0.6

    elif mode == "safety_regenerate":
        prompt = (
            f"{BASE_RULES}\n"
            f"{regional_section}\n"
            f"A previous attempt at this story had a safety issue: \"{feedback}\"\n"
            f"Write a completely new story from scratch that avoids this issue entirely — "
            f"do not reuse the previous premise or plot.\n\n"
            f"Story shape to follow: {arc['stages']}\n"
            f"Tone: {arc['tone']}\n"
            f"{COZY_WINDDOWN}\n\n"
            f"The child's original request: \"{user_request}\"\n\n"
            f"Now write the story."
        )
        temperature = 0.7

    else:
        raise ValueError(f"Unknown mode: {mode}")

    story_text = call_model(prompt, max_tokens=800, temperature=temperature)
    return {"story": story_text, "combo": arc["combo"]}

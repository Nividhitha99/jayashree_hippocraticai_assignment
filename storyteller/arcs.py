"""
Story arc templates: one per category. Each category defines a fixed
4-stage skeleton (introduce -> problem -> attempt -> resolve) plus
POOLS of variation options for setting/problem/resolution style, so
the same category doesn't produce the same story shape every time.
Stage 5 (cozy wind-down) stays identical across all categories.
"""

import random

COZY_WINDDOWN = (
    "End the story with a calm, gentle wind-down beat after the resolution — "
    "the character should end up relaxed, safe, and sleepy, not keyed up or excited. "
    "This is a bedtime story; the final feeling should be cozy and peaceful."
)

ARC_TEMPLATES = {
    "hero_adventure": {
        "skeleton": "1) Introduce the hero in {setting}. 2) {problem}. "
                    "3) The hero attempts to solve it. 4) The hero succeeds, resolving it through {resolution}.",
        "tone": "Resolve through courage and triumph, but keep stakes gentle and non-violent.",
        "settings": ["an enchanted forest", "a floating castle in the clouds", "a quiet mountain village", "an underwater kingdom"],
        "problems": ["A precious treasure has gone missing", "A friend is trapped and needs help", "A magical object has broken and needs fixing", "A tricky riddle is blocking the path forward"],
        "resolution": ["clever thinking", "teamwork with new friends", "an act of kindness", "quiet courage"],
    },
    "animal_jungle": {
        "skeleton": "1) Introduce an animal character in {setting}. 2) {problem}. "
                    "3) The animal explores and meets others along the way. 4) The problem resolves through {resolution}.",
        "tone": "Gentle and curious, resolving through kindness rather than conflict.",
        "settings": ["a lush jungle", "a sunny savanna", "a quiet forest clearing", "a riverside meadow"],
        "problems": ["A friend has wandered off and can't find the way home", "Food is hard to find this season", "A new animal has arrived and everyone is unsure of them", "Someone is feeling left out of the group"],
        "resolution": ["friendship", "cleverness", "sharing", "kindness"],
    },
    "family": {
        "skeleton": "1) Introduce a family in {setting}. 2) {problem}. "
                    "3) Family members talk about it or try something together. 4) It resolves through {resolution}.",
        "tone": "Warm and relatable, resolving through connection.",
        "settings": ["a cozy home", "a family road trip", "a backyard garden", "a weekend visit to grandparents"],
        "problems": ["Two siblings disagree about something", "Someone feels nervous about a new change", "A family tradition needs everyone's help", "Someone made a small mistake and feels bad about it"],
        "resolution": ["talking it out", "working together", "understanding each other's feelings", "a small act of forgiveness"],
    },
    "sports_inspirational": {
        "skeleton": "1) Introduce a character and {setting}. 2) {problem}. "
                    "3) The character practices, tries, or gets encouragement. 4) They grow through {resolution}.",
        "tone": "Encouraging and motivational; effort matters more than winning.",
        "settings": ["a soccer field", "a swimming pool", "a school track", "a neighborhood basketball court"],
        "problems": ["The character keeps losing and feels discouraged", "The character is nervous about a big upcoming game", "The character compares themselves to a more skilled friend", "The character wants to give up after a hard practice"],
        "resolution": ["persistence and practice", "encouragement from a friend", "focusing on effort instead of winning", "believing in themselves"],
    },
    "life_lesson": {
        "skeleton": "1) Introduce {setting}. 2) {problem}. "
                    "3) A gentle natural consequence or realization happens (never a punishment). 4) They learn through {resolution}.",
        "tone": "Warm and reflective, never preachy or punitive.",
        "settings": ["a relatable everyday moment at home", "snack time", "playtime with a sibling", "getting ready for bed"],
        "problems": ["The character wants too much of something not great for them", "The character isn't sure whether to tell the truth", "The character doesn't want to share a favorite toy", "The character rushes through a chore and it doesn't go well"],
        "resolution": ["a gentle realization", "a kind word from someone else", "seeing how their choice affected others", "trying again a better way"],
    },
    "general_fantasy": {
        "skeleton": "1) Introduce a character in {setting}. 2) {problem}. "
                    "3) The character explores or responds to it. 4) It resolves through {resolution}.",
        "tone": "Playful and imaginative; this is the fallback category for requests that don't fit elsewhere.",
        "settings": ["a hidden magical garden", "a sky full of floating islands", "a curious little town", "a starlit dreamscape"],
        "problems": ["Something wondrous and unexpected appears", "A puzzle needs solving to unlock something wonderful", "A new magical friend needs help", "A curious mystery needs uncovering"],
        "resolution": ["imagination", "curiosity", "a new friendship", "a clever idea"],
    },
}

CATEGORY_LIST = list(ARC_TEMPLATES.keys())


def get_arc(category: str, exclude_combo: tuple = None, force_combo: tuple = None) -> dict:
    """Return a fully-assembled arc for a category.

    force_combo: reuse an exact (setting, problem, resolution) tuple — used by
    "revise" mode so edits don't reshape the story's structural skeleton.
    exclude_combo: avoid repeating the last combo used for this category — used
    by "new" and "safety_regenerate" modes to prevent back-to-back identical arcs.
    """
    template = ARC_TEMPLATES.get(category, ARC_TEMPLATES["general_fantasy"])

    if force_combo is not None:
        setting, problem, resolution = force_combo
        combo = force_combo
    else:
        setting = random.choice(template["settings"])
        problem = random.choice(template["problems"])
        resolution = random.choice(template["resolution"])
        combo = (setting, problem, resolution)

        # Retry a few times if we hit the excluded combo, to avoid repetition
        attempts = 0
        while exclude_combo is not None and combo == exclude_combo and attempts < 5:
            setting = random.choice(template["settings"])
            problem = random.choice(template["problems"])
            resolution = random.choice(template["resolution"])
            combo = (setting, problem, resolution)
            attempts += 1

    stages = template["skeleton"].format(setting=setting, problem=problem, resolution=resolution)
    return {"stages": stages, "tone": template["tone"], "combo": combo}
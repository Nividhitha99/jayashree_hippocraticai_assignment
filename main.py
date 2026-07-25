import os
import openai

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

With more time, I'd fix the over-rewrite problem in revisions — right now,
asking for one small change (e.g. "make the lead a girl") sometimes causes
the model to reshuffle multiple characters and details instead of editing
just the requested element; a more constrained revision prompt (or a diff-style
edit) would fix this. I'd also improve regional accuracy — the "Indian" style
sometimes mixes in geographically inconsistent details (e.g. calling a setting
a "savanna" while adding Indian names), so I'd build region-specific setting
pools rather than relying on the model to self-correct terrain. I'd remove a
redundant categorize() API call in main.py (it currently categorizes once to
look up prior arc combos, then again inside run_pipeline). Finally, I'd persist
the "recently used arc combos" tracking to disk instead of only in-memory, so
repetition-avoidance works across separate program runs, not just one session.
"""

from storyteller.categorizer import categorize
from storyteller.generator import generate_story
from storyteller.judge import judge_story

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."

MAX_RETRIES = 2

SAFE_MODE_STORY = """Once there was a gentle bunny named Clover who loved quiet evenings.
Clover tidied up her cozy burrow, said goodnight to her woodland friends,
and curled up under a soft blanket of leaves. As the moon rose, Clover
closed her eyes, feeling calm, safe, and happy, and drifted off to a
peaceful sleep."""


def _pick_regional_style() -> str:
    """Prompt the user to pick a regional/cultural style. Returns the style
    string to pass to generate_story, or None for no preference."""
    print("\nPick a regional/cultural style for your story:")
    print("  1. Indian  (Indian names, villages, mango trees, monsoons...)")
    print("  2. Western/American  (the default North American feel)")
    print("  3. No preference  (let the story flow naturally)")
    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == "1":
            return "Indian"
        elif choice == "2":
            return "Western/American"
        elif choice == "3":
            return None
        else:
            print("Please enter 1, 2, or 3.")


def _next_mode(last_result: dict) -> str:
    """Decide what the next generation attempt should be, based on
    why the previous attempt failed."""
    if not last_result["safety_pass"]:
        return "safety_regenerate"
    return "revise"


def run_pipeline(user_request: str, exclude_combo: tuple = None, regional_style: str = None) -> dict:
    """Runs categorize -> generate -> judge -> retry loop.
    exclude_combo: the arc combo used last time for this category (if any),
    so we avoid repeating the same story shape back-to-back.
    regional_style: "Indian", "Western/American", or None.
    Returns the winning attempt (or the safe-mode fallback), including
    the combo actually used, so main() can track it for next time."""
    category = categorize(user_request)
    attempts = []

    gen = generate_story(user_request, category, mode="new",
                         exclude_combo=exclude_combo, regional_style=regional_style)
    story, combo = gen["story"], gen["combo"]
    result = judge_story(story)
    attempts.append({"story": story, "combo": combo, **result})

    tries = 0
    while not result["overall_pass"] and tries < MAX_RETRIES:
        mode = _next_mode(result)
        if mode == "revise":
            gen = generate_story(
                user_request, category, mode="revise",
                previous_story=story, feedback=result["feedback"], force_combo=combo,
                regional_style=regional_style,
            )
        else:  # safety_regenerate
            gen = generate_story(
                user_request, category, mode="safety_regenerate",
                feedback=result["feedback"], exclude_combo=combo,
                regional_style=regional_style,
            )
        story, combo = gen["story"], gen["combo"]
        result = judge_story(story)
        attempts.append({"story": story, "combo": combo, **result})
        tries += 1

    if result["overall_pass"]:
        return {"story": story, "category": category, "combo": combo, "source": "generated", "attempts": len(attempts)}

    safe_attempts = [a for a in attempts if a["safety_pass"]]
    if safe_attempts:
        best = max(safe_attempts, key=lambda a: a["weighted_score"])
        return {"story": best["story"], "category": category, "combo": best["combo"], "source": "best_effort", "attempts": len(attempts)}

    return {"story": SAFE_MODE_STORY, "category": category, "combo": None, "source": "safe_mode_fallback", "attempts": len(attempts)}


def main():
    last_combo_by_category = {}  # tracks the last arc combo used per category this session

    while True:
        user_input = input("What kind of story do you want to hear? ")
        regional_style = _pick_regional_style()

        # We don't know the category yet (that happens inside run_pipeline),
        # so we peek by categorizing here too, just to look up prior combo.
        # (Slightly redundant categorize() call, but keeps run_pipeline self-contained.)
        from storyteller.categorizer import categorize as _peek_categorize
        peeked_category = _peek_categorize(user_input)
        prior_combo = last_combo_by_category.get(peeked_category)

        outcome = run_pipeline(user_input, exclude_combo=prior_combo, regional_style=regional_style)
        if outcome["combo"] is not None:
            last_combo_by_category[outcome["category"]] = outcome["combo"]

        print("\n" + "=" * 50)
        print(outcome["story"])
        print("=" * 50)

        if outcome["source"] == "best_effort":
            print("\n(Note: this is our best attempt after a few tries.)")
        elif outcome["source"] == "safe_mode_fallback":
            print("\n(Note: we used a safe default story this time.)")

        while True:
            wants_changes = input("\nWould you like any changes to the story? (yes/no): ").strip().lower()
            if wants_changes not in ("yes", "y"):
                break
            change_request = input("What would you like changed? ")
            gen = generate_story(
                user_input, outcome["category"], mode="revise",
                previous_story=outcome["story"], feedback=change_request,
                force_combo=outcome["combo"],
                regional_style=regional_style,
            )
            result = judge_story(gen["story"])
            if result["safety_pass"]:
                outcome["story"] = gen["story"]
                print("\n" + "=" * 50)
                print(gen["story"])
                print("=" * 50)
            else:
                print("\nSorry, that change would make the story unsafe for kids — let's keep the previous version.")

        again = input("\nWould you like to hear another story? (yes/no): ").strip().lower()
        if again not in ("yes", "y"):
            print("\nGoodnight!")
            break


if __name__ == "__main__":
    main()

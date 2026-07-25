## The core problem being solved

A single LLM call asked to "write a good bedtime story" is unreliable — quality varies, and there's no mechanism to catch or fix a bad output. The whole system exists to add **quality control** and **structure** around a model that itself never changes.

## The main components

**1. Categorizer**
- Classifies the user's free-text request into one of 6 story categories (hero-adventure, animal/jungle, family, sports-inspirational, life-lesson, general/fantasy fallback)
- Done via an LLM call rather than keyword matching, because a request like "a girl who learns to be brave" has no adventure-related keywords but clearly belongs there — only genuine understanding catches that correctly

**2. Generator**
- Builds the actual story prompt using the category's "arc": a fixed 4-stage plot skeleton (introduce → problem → attempt → resolve), combined with a randomly-picked setting, problem, and resolution style from that category's pool
- The pool exists specifically so the same category doesn't produce the same story shape every time — a rigid single template collapses into repetition
- Also supports an optional regional/cultural style (Indian / Western-American / no preference)
- Every story ends with the same "cozy wind-down" beat, regardless of category, since these are bedtime stories

**3. Judge**
- A second LLM call that critiques the story against a rubric: readability, purpose, engagement, length, structure — each scored 1–10, combined into a weighted average
- **Safety is handled completely separately as a hard pass/fail gate** — never averaged in with quality scores, so a story can never "buy back" a safety failure with strong scores elsewhere
- If the judge's own response can't be parsed correctly, the system treats that as a safety failure rather than assuming the story is fine — fails safe, not open

## The retry logic

- If the judge fails a draft, the system checks *why* it failed and responds differently depending on the reason:
  - **Safety failure** → regenerate a brand new story from scratch, explicitly avoiding the flagged issue — patching an unsafe premise just papers over it
  - **Quality-only failure** → revise the existing draft with targeted feedback, preserving what already worked
- Capped at 2 retries total, to keep cost and latency bounded

## The fallback logic

- If retries run out without a pass: serve the best-scoring attempt, but **only from attempts that actually passed safety** — a high quality score can never make an unsafe draft the "winner"
- If nothing ever passed safety across all attempts, fall back to a fixed, pre-written safe story rather than risk showing anything model-generated

## The user feedback loop

- After a story is shown, the user can request changes
- Every revision is re-judged before being shown — if the requested change would make the story unsafe, the system refuses and keeps the previous version instead of complying blindly

## Why this design overall

- It demonstrates the **generator–critic pattern** (one call produces, another checks, code decides what happens next) — a common real-world pattern for adding reliability to LLM systems
- It treats **safety as categorically different from quality** throughout — never scored on the same scale, never averaged, never overridden by anything else, including user requests
- It adds variety (arc pools + repetition avoidance) and personalization (regional style) without touching the model itself — all the improvement comes from prompting and orchestration, per the assignment's constraint


___________________________________________________________________

# Hippocratic AI Coding Assignment
Welcome to the [Hippocratic AI](https://www.hippocraticai.com) coding assignment

## Instructions
The attached code is a simple python script skeleton. Your goal is to take any simple bedtime story request and use prompting to tell a story appropriate for ages 5 to 10.
- Incorporate a LLM judge to improve the quality of the story
- Provide a block diagram of the system you create that illustrates the flow of the prompts and the interaction between judge, storyteller, user, and any other components you add
- Do not change the openAI model that is being used. 
- Please use your own openAI key, but do not include it in your final submission.
- Otherwise, you may change any code you like or add any files

---

## Rules
- This assignment is open-ended
- You may use any resources you like with the following restrictions
   - They must be resources that would be available to you if you worked here (so no other humans, no closed AIs, no unlicensed code, etc.)
   - Allowed resources include but not limited to Stack overflow, random blogs, chatGPT et al
   - You have to be able to explain how the code works, even if chatGPT wrote it
- DO NOT PUSH THE API KEY TO GITHUB. OpenAI will automatically delete it

---

## What does "tell a story" mean?
It should be appropriate for ages 5-10. Other than that it's up to you. Here are some ideas to help get the brain-juices flowing!
- Use story arcs to tell better stories
- Allow the user to provide feedback or request changes
- Categorize the request and use a tailored generation strategy for each category

---

## How will I be evaluated
Good question. We want to know the following:
- The efficacy of the system you design to create a good story
- Are you comfortable using and writing a python script
- What kinds of prompting strategies and agent design strategies do you use
- Are the stories your tool creates good?
- Can you understand and deconstruct a problem
- Can you operate in an open-ended environment
- Can you surprise us

---

## Other FAQs
- How long should I spend on this? 
No more than 2-3 hours
- Can I change what the input is? 
Sure
- How long should the story be?
You decide
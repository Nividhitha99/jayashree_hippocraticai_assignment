"""
Thin wrapper around the OpenAI ChatCompletion call. Every other module
in this project (categorizer, generator, judge) calls through this one
function, so there's a single place that actually talks to OpenAI.
"""

import os
import openai


def call_model(prompt: str, max_tokens: int = 3000, temperature: float = 0.1) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY","").strip()  # please use your own openai api key here.
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]  # type: ignore
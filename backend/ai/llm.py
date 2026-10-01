"""LLM integration point — YOUR implementation goes here.

This is the single file to wire up a real generative model. Everything
else in the backend calls through this module, so swapping providers
(OpenAI / Gemini / Claude / local Ollama) only touches this file.

Usage once implemented:
    from ai.llm import complete_structured
    items = complete_structured(
        prompt="Extract the ordered items ...",
        schema=[{"product_name": str, "quantity": float, "price_unit": float}],
    )

Example implementation (uncomment + `pip install openai` + set LLM_API_KEY):

    from openai import OpenAI
    client = OpenAI(api_key=LLM_API_KEY)

    def complete(prompt, system=None, temperature=0.0):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(model=LLM_MODEL, messages=messages,
                                              temperature=temperature)
        return resp.choices[0].message.content

    def complete_structured(prompt, schema, system=None):
        # Ask the model to return strict JSON matching `schema`, then json.loads it.
        ...
"""
from config import LLM_API_KEY, LLM_MODEL  # noqa: F401  (available for your implementation)


class LLMNotConfigured(Exception):
    """Raised when AI code path needs the LLM but no provider is wired up."""


def complete(prompt, system=None, temperature=0.0):
    """TODO: implement with your chosen provider (see module docstring)."""
    raise LLMNotConfigured(
        "No LLM provider configured. Implement ai/llm.py (OpenAI example in its docstring)."
    )


def complete_structured(prompt, schema, system=None):
    """TODO: structured-output call.

    `schema` is a list like [{"product_name": str, "quantity": float, ...}];
    the function must return a list of dicts with exactly those keys.
    This is what makes the AI AGENTIC: the model outputs machine-readable
    tool decisions instead of prose.
    """
    raise LLMNotConfigured(
        "No LLM provider configured. Implement complete_structured() in ai/llm.py."
    )

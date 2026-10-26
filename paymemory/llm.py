"""Groq LLM helper with retries and a fallback model (function/API errors happen)."""
import os
import re
import time

from groq import Groq

MODELS = [os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"), "qwen/qwen3-32b"]

BASE_RULES = (
    "You write short payment reminder messages (WhatsApp or email style, under 120 words) "
    "for a small Indian business. Be professional and human. Sign off as 'Accounts Team'. "
    "Output ONLY the message text."
)


def _chat(system: str, user: str, retries: int = 2) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    last_error = None
    for model in MODELS:
        for attempt in range(retries):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    temperature=0.4,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                text = resp.choices[0].message.content or ""
                text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
                return text.strip()
            except Exception as e:  # rate limit, model error, network...
                last_error = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after retries: {last_error}")


def draft_reminder(customer: str, invoice: dict, memories: list[str] | None) -> str:
    inv = (
        f"Customer: {customer}\nInvoice {invoice['id']}: Rs {invoice['amount']:,}, "
        f"due {invoice['due_date']}, {invoice['days_overdue']} days overdue."
    )
    if not memories:
        return _chat(BASE_RULES, f"Write a payment reminder.\n{inv}")

    history = "\n".join(f"- {m}" for m in memories)
    system = (
        BASE_RULES
        + " You are given this customer's remembered history. Use it naturally: reference "
        "past promises, match the tone and channel that worked, and avoid what failed. "
        "Never invent facts that are not in the history."
    )
    return _chat(system, f"Write a payment reminder.\n{inv}\n\nRemembered history:\n{history}")

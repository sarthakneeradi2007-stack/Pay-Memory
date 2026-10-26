"""Thin wrapper around Hindsight. One memory bank per customer.

Streamlit already runs an asyncio event loop in its script thread, and the
Hindsight sync client needs a loop-free thread. So every call below runs in a
fresh worker thread with its own client (see _run).
"""
import os
import re
from concurrent.futures import ThreadPoolExecutor

from hindsight_client import Hindsight

MISSION = (
    "I am a polite but persistent accounts-receivable assistant for a small business. "
    "I remember how each customer pays: their promises, whether they kept them, "
    "which tone and channel worked, and any disputes. I use this history to recommend "
    "how to follow up on overdue invoices."
)
CONTEXT = "customer payment history and collections follow-up"


def _run(fn):
    """Run fn(client) in a separate thread with a fresh Hindsight client."""
    base_url = os.getenv("HINDSIGHT_BASE_URL")
    if not base_url:
        raise RuntimeError("HINDSIGHT_BASE_URL is missing. Add it to your .env file.")
    api_key = os.getenv("HINDSIGHT_API_KEY")

    def job():
        with Hindsight(base_url=base_url, api_key=api_key, timeout=120) as client:
            return fn(client)

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(job).result()


def bank_id_for(customer_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", customer_name.lower()).strip("-")
    return f"paymemory-{slug}"


def _ensure_bank(client, customer_name: str) -> str:
    """Create the customer's memory bank (safe to call repeatedly)."""
    bank_id = bank_id_for(customer_name)
    try:
        client.create_bank(bank_id=bank_id, name=customer_name, mission=MISSION)
    except Exception:
        pass  # most likely the bank already exists
    return bank_id


def load_history(customer_name: str, events: list[str]) -> None:
    """RETAIN: store a customer's past events in memory."""
    def op(client):
        bank_id = _ensure_bank(client, customer_name)
        items = [{"content": e, "context": CONTEXT} for e in events]
        client.retain_batch(bank_id=bank_id, items=items, retain_async=False)
    _run(op)


def log_event(customer_name: str, text: str) -> None:
    """RETAIN: store one new event (e.g. today's outcome)."""
    def op(client):
        bank_id = _ensure_bank(client, customer_name)
        client.retain(bank_id=bank_id, content=text, context=CONTEXT, retain_async=False)
    _run(op)


def recall_history(customer_name: str, query: str) -> list[str]:
    """RECALL: search this customer's memory."""
    def op(client):
        bank_id = _ensure_bank(client, customer_name)
        result = client.recall(bank_id=bank_id, query=query, budget="mid")
        return [r.text for r in result.results]
    return _run(op)


def strategy(customer_name: str, invoice_summary: str) -> str:
    """REFLECT: ask Hindsight to reason over memory and recommend an approach."""
    def op(client):
        bank_id = _ensure_bank(client, customer_name)
        answer = client.reflect(
            bank_id=bank_id,
            query=(
                f"What is the best way to follow up with {customer_name} about this overdue "
                "invoice? Consider their past promises, what worked before, tone and channel."
            ),
            context=invoice_summary,
            budget="low",
        )
        return answer.text
    return _run(op)

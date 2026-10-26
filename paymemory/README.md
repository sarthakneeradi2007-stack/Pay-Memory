# 💸 PayMemory

**An AI collections agent that remembers how every customer pays.**

Small businesses lose time and cash chasing late invoices with generic reminders, because nobody remembers who promised what, who ghosted, and which follow-up style actually gets each customer to pay. PayMemory uses **Hindsight memory** to learn every customer's payment behavior, broken promises, disputes, and best-working follow-up approach, so each reminder gets smarter over time.

Built for **Hack with Hyderabad 3.0** (AI Agents That Learn Using Hindsight).

## How Hindsight memory is used

| Hindsight feature | How PayMemory uses it |
|---|---|
| **Memory banks** | One bank per customer (`paymemory-<name>`), configured with a collections-assistant mission |
| **`retain`** | Stores past payment history and every new outcome logged in the app (promises, broken promises, disputes, what channel worked) |
| **`recall`** | Before drafting a reminder, recalls the customer's history so the message is personalized |
| **`reflect`** | Reasons over the whole history to recommend a follow-up strategy |
| **Observations** | Hindsight automatically consolidates facts into patterns (e.g. "slips promised dates by 1 to 2 weeks") |

**Before/after:** the app shows a generic reminder (memory OFF) next to a personalized one (memory ON) for the same invoice. Log a new outcome and the next draft and strategy change.

## Tech stack
Python, Streamlit, Hindsight Cloud (`hindsight-client`), Groq (`openai/gpt-oss-120b`, fallback `qwen/qwen3-32b`).

## Run it

```bash
git clone <this-repo-url>
cd <repo-folder>
python -m venv venv
# Windows: venv\Scripts\activate    Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Windows: copy .env.example .env  (then fill in your keys)
python test_hindsight.py   # checks your Hindsight connection
streamlit run app.py
```

## Demo flow
1. Click **Load sample history** in the sidebar.
2. Pick **Ravi Kumar** and click **Draft reminders**: compare generic vs memory-powered.
3. Click **Get strategy** to see Hindsight `reflect`.
4. **Log an outcome**, draft again, and watch the agent adapt.
5. Click **Show memory** to see what the agent remembers.

## Project structure
```
app.py            Streamlit UI
memory.py         Hindsight wrapper (retain / recall / reflect)
llm.py            Groq LLM helper with retries and fallback model
data/customers.json   Synthetic customers and payment histories
test_hindsight.py Connection check
```

## Business model
Subscription for small businesses, agencies and distributors (for example tiered by number of customers), with a possible success fee on recovered payments. The longer a business uses it, the more the agent knows its customers.

## Team
<add your name(s) here>

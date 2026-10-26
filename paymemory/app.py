"""PayMemory: an AI collections agent that remembers how every customer pays."""
import json
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

import llm
import memory

load_dotenv()
st.set_page_config(page_title="PayMemory", page_icon="💸", layout="wide")

customers = json.loads(Path("data/customers.json").read_text(encoding="utf-8"))
by_name = {c["name"]: c for c in customers}

st.title("💸 PayMemory")
st.caption("An AI collections agent that remembers how every customer pays. Powered by Hindsight memory + Groq.")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Customers")
    name = st.selectbox("Select customer", list(by_name.keys()))
    st.divider()
    st.markdown("**Step 1:** load sample payment history into Hindsight memory.")
    if st.button("Load sample history (all customers)"):
        try:
            with st.spinner("Retaining memories in Hindsight (this can take a minute)..."):
                for c in customers:
                    memory.load_history(c["name"], c["history"])
            st.success("Memory loaded!")
        except Exception as e:
            st.error(f"Could not load memory: {e}")

cust = by_name[name]
inv = cust["invoice"]

# ---------- Invoice ----------
st.subheader(f"{cust['name']} ({cust['company']})")
c1, c2, c3 = st.columns(3)
c1.metric("Invoice", inv["id"])
c2.metric("Amount", f"Rs {inv['amount']:,}")
c3.metric("Days overdue", inv["days_overdue"])

# ---------- Draft: memory OFF vs ON ----------
st.markdown("### Draft a reminder: without memory vs with memory")
if st.button("Draft reminders", type="primary"):
    left, right = st.columns(2)
    with left:
        st.markdown("#### 🚫 Memory OFF (generic)")
        try:
            with st.spinner("Drafting..."):
                st.info(llm.draft_reminder(cust["name"], inv, None))
        except Exception as e:
            st.error(str(e))
    with right:
        st.markdown("#### 🧠 Memory ON (Hindsight)")
        try:
            with st.spinner("Recalling history and drafting..."):
                mems = memory.recall_history(
                    cust["name"],
                    "payment history, promises made, what worked, preferred tone and channel",
                )
                if not mems:
                    st.warning("No memories found yet. Click 'Load sample history' in the sidebar first.")
                st.success(llm.draft_reminder(cust["name"], inv, mems))
        except Exception as e:
            st.error(str(e))

# ---------- Strategy ----------
st.markdown("### Recommended strategy (Hindsight reflect)")
if st.button("Get strategy"):
    try:
        summary = (f"Invoice {inv['id']} for Rs {inv['amount']:,}, "
                   f"{inv['days_overdue']} days overdue.")
        with st.spinner("Reflecting on memory..."):
            st.write(memory.strategy(cust["name"], summary))
    except Exception as e:
        st.error(str(e))

# ---------- Log outcome ----------
st.markdown("### Log what happened (the agent learns from this)")
with st.form("log_outcome", clear_on_submit=True):
    outcome = st.selectbox(
        "Outcome",
        ["Paid in full", "Promised to pay by a date", "Promise broken", "Ignored the reminder",
         "Raised a dispute", "Paid after a phone call"],
    )
    notes = st.text_input("Details (e.g. channel used, promised date, what the customer said)")
    submitted = st.form_submit_button("Save to memory")
    if submitted:
        try:
            text = f"On {date.today().isoformat()}, regarding invoice {inv['id']} for {cust['name']}: {outcome}. {notes}"
            memory.log_event(cust["name"], text)
            st.success("Saved. The agent will remember this next time.")
        except Exception as e:
            st.error(str(e))

# ---------- Memory panel ----------
st.markdown("### 🧠 What the agent remembers")
if st.button("Show memory"):
    try:
        with st.spinner("Recalling..."):
            mems = memory.recall_history(
                cust["name"], "everything about this customer's payment behavior"
            )
        if mems:
            for m in mems:
                st.markdown(f"- {m}")
        else:
            st.info("Nothing remembered yet. Load the sample history from the sidebar.")
    except Exception as e:
        st.error(str(e))

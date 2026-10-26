"""Run this first to check your Hindsight connection: python test_hindsight.py"""
from dotenv import load_dotenv

import memory

load_dotenv()
memory.log_event("Test Customer", "Test Customer promised to pay Rs 10,000 by Friday but did not.")
print("Recall result:")
for t in memory.recall_history("Test Customer", "What did this customer promise?"):
    print("-", t)

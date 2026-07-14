import json
import logging
from src.pipeline.rag_chain import ask
from src.pipeline.retriever import detect_scheme

# Minimal logging
logging.basicConfig(level=logging.WARNING)

def run_eval():
    with open("tests/test_queries.json", "r") as f:
        queries = json.load(f)

    total = len(queries)
    passed_refusals = 0
    total_refusals = 0
    passed_schemes = 0
    total_factuals = 0

    print(f"Starting evaluation of {total} queries...")
    
    for item in queries:
        q = item["query"]
        q_type = item["type"]
        
        if q_type in ["advisory", "pii"]:
            total_refusals += 1
            res = ask(q)
            if res.get("type") in ["refusal", "pii_refusal"]:
                passed_refusals += 1
            else:
                print(f"[FAIL Refusal] Query: {q}")
                print(f"  Got: {res.get('type')}")
        
        elif q_type == "factual":
            total_factuals += 1
            expected = item.get("expected_scheme")
            
            # Since generating an LLM response for 20+ queries is slow and costs API credits,
            # we will evaluate the *retriever accuracy* here by checking detect_scheme
            detected = detect_scheme(q)
            if detected == expected:
                passed_schemes += 1
            else:
                print(f"[FAIL Scheme] Query: {q}")
                print(f"  Expected: {expected}")
                print(f"  Got: {detected}")

    print("\n================== EVALUATION RESULTS ==================")
    if total_refusals > 0:
        print(f"Refusal Accuracy: {passed_refusals}/{total_refusals} ({(passed_refusals/total_refusals)*100:.1f}%)")
    if total_factuals > 0:
        print(f"Scheme Detection (Retrieval) Accuracy: {passed_schemes}/{total_factuals} ({(passed_schemes/total_factuals)*100:.1f}%)")

if __name__ == "__main__":
    run_eval()

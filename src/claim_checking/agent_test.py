
import time

from agent_search import verify_claim_with_variants
from claim_similarity import filter_rephrasings_by_similarity
from rephraser import rephrase_claim_v2
import yaml


def load_config(path=".\config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

extracted_claims = [
    {"claim": "لون أشعة الشمس أصفر", "time_stamp": "00:01:12"},
    {"claim": "عمر النظام الشمسي هو 13.8 مليار سنة", "time_stamp": "00:02:45"},
    {"claim": "الضوء هو شكل من أشكال الطاقة", "time_stamp": "00:04:10"},
]

claims = [item["claim"] for item in extracted_claims]


rephrased_outputs = rephrase_claim_v2(claims, language= config["fact_checking"]["Search"]["language"], n_variants=config["fact_checking"]["rephrasing"]["n_variants"])
rephrased_lists = [entry["rephrased"] for entry in rephrased_outputs]
filtered_results = filter_rephrasings_by_similarity(
    claims=[entry["original"] for entry in rephrased_outputs],
    rephrasings=rephrased_lists,
    threshold=config["fact_checking"]["check_similarity"]["threshold"],
    top_k= config["fact_checking"]["check_similarity"]["top_k"]
)


facts = []
for entry in filtered_results:
    original = entry["original"]
    variants_2 = entry["selected_variants"]
    timestamp = next(
        (item["time_stamp"] for item in extracted_claims if item["claim"] == original),
        None
    )
    final_decision = verify_claim_with_variants(original, language= config["fact_checking"]["Search"]["language"], variants = variants_2)
    facts.append(final_decision) 
    final_decision["time_stamp"] = timestamp
    time.sleep(30) 

for fact in facts:
    print(f"\n🔹 Original Claim: {fact['claim']} (⏱️ {fact['time_stamp']})")
    print(f"Final Answer: {fact['status']}")
    print(f"Explanation: {fact['explanation']}")
    if fact['sources']:
        print("Sources:")
        for idx, source in enumerate(fact['sources'], 1):
            print(f"  {idx}. {source['title']} - {source['url']}")
    else:
        print("No sources available.")
    print("-" * 60)
    
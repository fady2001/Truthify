import time
from typing import List

from claim_checking.agent_search import verify_claim_with_variants
from claim_checking.claim_similarity import filter_rephrasings_by_similarity
from claim_checking.rephraser import rephrase_claim_v2
from claim_extraction.langgraph_pipeline import run_truthify_pipeline
from claim_extraction.schemas import PotentialClaim


async def main():
    """Example usage of the LangGraph Truthify pipeline."""
    input_text = (
        "The Earth is flat. The moon landing was staged. "
        "COVID-19 is caused by 5G technology."
    )
    claims:List[PotentialClaim] = await run_truthify_pipeline(input_text)
    claims = [claim.claim_text for claim in claims]
    rephrased_outputs = rephrase_claim_v2(claims, language="Arabic", n_variants=5)
    rephrased_lists = [entry["rephrased"] for entry in rephrased_outputs]
    filtered_results = filter_rephrasings_by_similarity(
        claims=[entry["original"] for entry in rephrased_outputs],
        rephrasings=rephrased_lists,
        threshold=0.8,
        top_k=2
    )


    facts = []
    for entry in filtered_results:
        original = entry["original"]
        variants = entry["selected_variants"]
        # timestamp = next(
        #     (item["time_stamp"] for item in claims if item["claim"] == original),
        #     None
        # )
        final_decision = verify_claim_with_variants(original, "Arabic", variants)
        facts.append(final_decision) 
        # final_decision["time_stamp"] = timestamp
        time.sleep(30) 

if __name__ == "__main__":
    import asyncio
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Run the main function to demonstrate the pipeline
    asyncio.run(main())
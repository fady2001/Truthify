from typing import Dict, List

from langchain.prompts import ChatPromptTemplate
from loguru import logger

from prompts import DECOMPOSITION_SYSTEM_PROMPT, HUMAN_PROMPT
from schemas import DecompositionOutput, DisambiguatedContent, PotentialClaim, State
from utils import get_llm


async def decomposition_stage(disambiguated_item: DisambiguatedContent) -> List[PotentialClaim]:
    """Extract atomic claims from a disambiguated sentence.

    Args:
        disambiguated_item: Disambiguated content to process

    Returns:
        List of potential claims
    """
    sentence_to_decompose = disambiguated_item.disambiguated_sentence
    logger.debug(f"Processing decomposition for: '{sentence_to_decompose}'")

    # Get zero-temp LLM for consistent results
    llm_instance = get_llm(0)

    # Get context without following sentences
    original_context = disambiguated_item.original_selected_item.original_context_item.context
    prompt_template = ChatPromptTemplate(
        [
            ("system", DECOMPOSITION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )
    prompt_messages = prompt_template.invoke(
        {
            "excerpt": original_context,
            "sentence": sentence_to_decompose,
        }
    )
    decomposition_response = llm_instance.with_structured_output(DecompositionOutput).invoke(
        prompt_messages
    )

    # If no claims were found
    if (
        not decomposition_response
        or decomposition_response.no_claims
        or not decomposition_response.claims
    ):
        logger.info(f"No claims found in: '{sentence_to_decompose}'")
        return []

    logger.debug(f"Decomposition response: {decomposition_response}")

    # Clean up claims and convert to objects
    extracted_claim_texts = [
        claim.strip() for claim in decomposition_response.claims if claim.strip()
    ]

    # Get original sentence and index
    original_sentence = disambiguated_item.original_selected_item.original_context_item.sentence
    original_sentence_index = disambiguated_item.original_selected_item.original_context_item.index

    potential_claims = [
        PotentialClaim(
            claim_text=claim_text,
            disambiguated_sentence=sentence_to_decompose,
            original_sentence=original_sentence,
            original_index=original_sentence_index,
        )
        for claim_text in extracted_claim_texts
    ]

    logger.info(
        f"Extracted {len(potential_claims)} potential claims from: '{sentence_to_decompose}'"
    )
    return potential_claims


async def decomposition_node(state: State) -> Dict[str, List[PotentialClaim]]:
    """Node function to decompose disambiguated content into potential claims."""
    # Get the disambiguated contents from the state
    disambiguated_contents = state.disambiguated_contents

    # Process each disambiguated content to extract claims
    all_potential_claims = []
    for disambiguated_item in disambiguated_contents:
        claims = await decomposition_stage(disambiguated_item)
        all_potential_claims.extend(claims)

    return {"potential_claims": all_potential_claims}

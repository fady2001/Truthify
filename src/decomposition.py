from typing import List

from langchain.prompts import ChatPromptTemplate
from loguru import logger

from prompts import DECOMPOSITION_SYSTEM_PROMPT, HUMAN_PROMPT
from schemas import DecompositionOutput, DisambiguatedContent, PotentialClaim
from utils import get_llm


async def decomposition_stage(disambiguated_item: DisambiguatedContent) -> List[PotentialClaim]:
    """Extract atomic claims from a disambiguated sentence.

    Args:
        disambiguated_item: Disambiguated content to process

    Returns:
        List of potential claims
    """
    sentence = disambiguated_item.disambiguated_sentence
    logger.debug(f"Processing decomposition for: '{sentence}'")

    # Get zero-temp LLM for consistent results
    llm = get_llm(0)

    # Get context without following sentences
    original_context = (
        disambiguated_item.original_selected_item.original_context_item.context
    )
    message = ChatPromptTemplate(
        [
            ("system", DECOMPOSITION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )
    prompt_messages = message.invoke(
        {
            "excerpt": original_context,
            "sentence": sentence,
        }
    )
    response = llm.with_structured_output(DecompositionOutput).invoke(prompt_messages)

    # If no claims were found
    if not response or response.no_claims or not response.claims:
        logger.info(f"No claims found in: '{sentence}'")
        return []

    logger.debug(f"Decomposition response: {response}")

    # Clean up claims and convert to objects
    claims_texts = [claim.strip() for claim in response.claims if claim.strip()]

    # Get original sentence and index
    original_sentence = disambiguated_item.original_selected_item.original_context_item.original_sentence
    original_index = disambiguated_item.original_selected_item.original_context_item.original_index

    potential_claims = [
        PotentialClaim(
            claim_text=claim_text, 
            disambiguated_sentence=sentence,
            original_sentence=original_sentence,
            original_index=original_index
        )
        for claim_text in claims_texts
    ]

    logger.info(
        f"Extracted {len(potential_claims)} potential claims from: '{sentence}'"
    )
    return potential_claims
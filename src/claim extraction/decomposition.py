from typing import Dict, List

from langchain.prompts import ChatPromptTemplate
from prompts import DECOMPOSITION_SYSTEM_PROMPT, HUMAN_PROMPT
from schemas import (
    BatchDecompositionOutput,
    DisambiguatedContent,
    PotentialClaim,
    State,
)
from utils import format_excerpt_sentence_pairs, get_llm


async def decomposition_stage(disambiguated_items: List[DisambiguatedContent]) -> List[PotentialClaim]:
    """Extract atomic claims from a disambiguated sentence.

    Args:
        disambiguated_item: Disambiguated content to process

    Returns:
        List of potential claims
    """
    # Get zero-temp LLM for consistent results
    llm_instance = get_llm(0)
    # llm_instance = get_ollama(0)

    # Get context without following sentences
    prompt_template = ChatPromptTemplate(
        [
            ("system", DECOMPOSITION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )
    excerpts = [disambiguated_item.original_selected_item.original_context_item.context for disambiguated_item in disambiguated_items]
    sentence_to_decomposes = [disambiguated_item.disambiguated_sentence for disambiguated_item in disambiguated_items]
    
    prompt_messages = prompt_template.invoke(
        {
            "excerpt_sentence_pairs": format_excerpt_sentence_pairs(excerpts, sentence_to_decomposes)
        }
    )
    
    batch_decomposition_response:BatchDecompositionOutput = llm_instance.with_structured_output(BatchDecompositionOutput).invoke(
        prompt_messages
    )

    claims = []
    decomposition_outputs = batch_decomposition_response.decomposition_outputs
    if (
        not batch_decomposition_response
        or not batch_decomposition_response.decomposition_outputs
    ):
        return []
    for i in range(len(decomposition_outputs)):
        potential_claims = [
            PotentialClaim(claim_text=claim.strip()) for claim in decomposition_outputs[i].claims if claim.strip()
        ]
        claims.extend(potential_claims)
    return claims


async def decomposition_node(state: State) -> Dict[str, List[PotentialClaim]]:
    """Node function to decompose disambiguated content into potential claims."""
    # Get the disambiguated contents from the state
    batch_size = 100
    disambiguated_contents = state.disambiguated_contents
    all_potential_claims = []
    for batch_start in range(0, len(disambiguated_contents), batch_size):
        batch_end = min(batch_start + batch_size, len(disambiguated_contents))
        batch = disambiguated_contents[batch_start:batch_end]
        if not batch:
            continue
        all_potential_claims = await decomposition_stage(batch)
    return {"potential_claims": all_potential_claims}

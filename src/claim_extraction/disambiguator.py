from typing import Dict, List, Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from loguru import logger
from .prompts import DISAMBIGUATION_SYSTEM_PROMPT, HUMAN_PROMPT
from .schemas import (
    BatchDisambiguationOutput,
    DisambiguatedContent,
    SelectedContent,
    State,
)
from .utils import batch_voting, format_excerpt_sentence_pairs, get_llm


async def single_disambiguation_attempt(
    selected_items: List[SelectedContent], llm_instance: BaseChatModel
) -> Tuple[List[bool], List[Optional[str]]]:
    """Try to disambiguate a single sentence.

    Args:
        selected_item: Selected content to disambiguate
        llm_instance: LLM instance

    Returns:
        (success, disambiguated_sentence)
    """
    prompt_template = ChatPromptTemplate(
        [
            ("system", DISAMBIGUATION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    prompt_messages = prompt_template.invoke(
        {
            "excerpt_sentence_pairs": format_excerpt_sentence_pairs(
                [selected_item.original_context_item.context for selected_item in selected_items],
                [selected_item.processed_sentence for selected_item in selected_items],
            )
        }
    )

    # Call the LLM
    batch_disambiguation_response: BatchDisambiguationOutput = llm_instance.with_structured_output(
        BatchDisambiguationOutput
    ).invoke(prompt_messages)

    # Skip sentences we can't disambiguate - better to drop them
    # than have unclear claims
    flags: List[bool] = []
    disambiguated_sentences: List[Optional[str]] = []
    disambiguated_contents = batch_disambiguation_response.disambiguated_contents
    if (
        not batch_disambiguation_response
        or not batch_disambiguation_response.disambiguated_contents
    ):
        return [False], [None]
    for i in range(len(disambiguated_contents)):
        if (
            not disambiguated_contents[i].disambiguated_sentence
            or disambiguated_contents[i].cannot_be_disambiguated
        ):
            flags.append(False)
            disambiguated_sentences.append(None)
        else:
            disambiguated_sentences.append(
                disambiguated_contents[i].disambiguated_sentence.strip()
            )
            flags.append(True)
    return flags, disambiguated_sentences


def create_disambiguated_content(
    disambiguated_sentence: str, selected_item: SelectedContent
) -> DisambiguatedContent:
    """Package the disambiguated content.

    Args:
        disambiguated_sentence: Sentence with resolved references
        selected_item: Original selected content

    Returns:
        DisambiguatedContent object
    """
    original_sentence = selected_item.processed_sentence
    logger.info(f"Disambiguated: '{original_sentence}' → '{disambiguated_sentence}'")
    return DisambiguatedContent(
        disambiguated_sentence=disambiguated_sentence,
        original_selected_item=selected_item,
    )


def create_batch_disambiguated_content(
    disambiguated_sentences: List[str], selected_items: List[SelectedContent]
) -> List[DisambiguatedContent]:
    """Create a batch of disambiguated content.

    Args:
        disambiguated_sentences: List of disambiguated sentences
        selected_items: List of original selected content

    Returns:
        List of DisambiguatedContent objects
    """
    return [
        DisambiguatedContent(
            disambiguated_sentence=disambiguated_sentence, original_selected_item=selected_item
        )
        for disambiguated_sentence, selected_item in zip(disambiguated_sentences, selected_items)
    ]


async def disambiguator_node(state: State) -> Dict[str, List[DisambiguatedContent]]:
    """Node function to disambiguate selected content."""
    # Get the selected contents from the state
    selected_contents = state.selected_contents

    # Get LLM instance
    llm_instance = get_llm(1)
    # llm_instance = get_ollama(1)

    disambiguated_results = await batch_voting(
        items=selected_contents,
        single_attempt_function=single_disambiguation_attempt,
        llm_instance=llm_instance,
        num_completions=1,
        min_successes=1,
        result_factory=create_batch_disambiguated_content,
        description="Disambiguating selected sentences.",
        batch_size=100,
    )

    return {"disambiguated_contents": disambiguated_results}

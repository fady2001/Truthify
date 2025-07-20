import asyncio
from typing import Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from loguru import logger

from prompts import DISAMBIGUATION_SYSTEM_PROMPT, HUMAN_PROMPT
from schemas import DisambiguatedContent, DisambiguationOutput, SelectedContent
from utils import get_llm, voting


async def single_disambiguation_attempt(
    selected_item: SelectedContent, llm_instance: BaseChatModel
) -> Tuple[bool, Optional[str]]:
    """Try to disambiguate a single sentence.

    Args:
        selected_item: Selected content to disambiguate
        llm_instance: LLM instance

    Returns:
        (success, disambiguated_sentence)
    """
    sentence_to_disambiguate = selected_item.processed_sentence

    prompt_template = ChatPromptTemplate(
        [
            ("system", DISAMBIGUATION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    prompt_messages = prompt_template.invoke(
        {
            "excerpt": selected_item.original_context_item.context,
            "sentence": sentence_to_disambiguate,
        }
    )

    # Call the LLM
    disambiguation_response: DisambiguationOutput = llm_instance.with_structured_output(
        DisambiguationOutput
    ).invoke(prompt_messages)

    # Skip sentences we can't disambiguate - better to drop them
    # than have unclear claims
    if (
        not disambiguation_response
        or not disambiguation_response.disambiguated_sentence
        or disambiguation_response.cannot_be_disambiguated
    ):
        return False, None

    return True, disambiguation_response.disambiguated_sentence.strip()


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


async def main():
    llm_instance = get_llm(1)

    sample_text = "Alice and Bob went to the park. She loves to play there. They had a great time."

    from selector import create_selected_content, single_selection_attempt
    from splitter import sentence_splitter

    contextual_sentences = sentence_splitter(sample_text)

    # Properly run the async voting function
    selected_items = await voting(
        items=contextual_sentences,
        single_attempt_function=single_selection_attempt,
        llm_instance=llm_instance,
        num_completions=3,
        min_successes=2,
        result_factory=create_selected_content,
        description="Selecting sentences from a text that are verifiable claims.",
    )

    disambiguated_results = await voting(
        items=selected_items,
        single_attempt_function=single_disambiguation_attempt,
        llm_instance=llm_instance,
        num_completions=1,
        min_successes=1,
        result_factory=create_disambiguated_content,
        description="Disambiguating selected sentences.",
    )

    for disambiguated_item in disambiguated_results:
        print(disambiguated_item)


if __name__ == "__main__":
    asyncio.run(main())

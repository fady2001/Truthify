import asyncio
from typing import Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from loguru import logger

from prompts import DISAMBIGUATION_SYSTEM_PROMPT, HUMAN_PROMPT
from schemas import DisambiguatedContent, DisambiguationOutput, SelectedContent
from utils import get_llm, voting


async def single_disambiguation_attempt(selected_item: SelectedContent, llm_instance: BaseChatModel) -> Tuple[bool, Optional[str]]:
    """Try to disambiguate a single sentence.

    Args:
        selected_item: Selected content to disambiguate
        llm: LLM instance

    Returns:
        (success, disambiguated_sentence)
    """
    sentence = selected_item.processed_sentence
    
    messages = ChatPromptTemplate(
        [
            ("system", DISAMBIGUATION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    prompt_messages = messages.invoke(
        {
            "excerpt": selected_item.original_context_item.context,
            "sentence": sentence,
        }
    )


    # Call the LLM
    response:DisambiguationOutput = llm_instance.with_structured_output(DisambiguationOutput).invoke(prompt_messages)

    # Skip sentences we can't disambiguate - better to drop them
    # than have unclear claims
    if (
        not response
        or not response.disambiguated_sentence
        or response.cannot_be_disambiguated
    ):
        return False, None

    return True, response.disambiguated_sentence.strip()
        
def create_disambiguated_content(disambiguated_sentence: str, selected_item: SelectedContent) -> DisambiguatedContent:
    """Package the disambiguated content.

    Args:
        disambiguated_sentence: Sentence with resolved references
        selected_item: Original selected content

    Returns:
        DisambiguatedContent object
    """
    sentence = selected_item.processed_sentence
    logger.info(f"Disambiguated: '{sentence}' → '{disambiguated_sentence}'")
    return DisambiguatedContent(
        disambiguated_sentence=disambiguated_sentence,
        original_selected_item=selected_item,
    )


async def main():
    llm = get_llm(1)

    text = (
        "Alice and Bob went to the park. "
        "She loves to play there. "
        "They had a great time."
    )

    from selector import create_selected_content, single_selection_attempt
    from splitter import sentence_splitter

    sentences = sentence_splitter(text)
    
    # Properly run the async voting function
    selected_items = await voting(
        items=sentences,
        single_attempt_function=single_selection_attempt,
        llm=llm,
        completions=3,
        min_successes=2,
        result_factory=create_selected_content,
        description="Selecting sentences from a text that are verifiable claims."
    )

    disambiguated_results = await voting(
        items=selected_items,
        single_attempt_function=single_disambiguation_attempt,
        llm=llm,
        completions=1,
        min_successes=1,
        result_factory=create_disambiguated_content,
        description="Disambiguating selected sentences."
    )

    for item in disambiguated_results:
        print(item)

if __name__ == "__main__":
    asyncio.run(main())
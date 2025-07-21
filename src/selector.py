from typing import Dict, List, Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

from prompts import HUMAN_PROMPT, SELECTION_SYSTEM_PROMPT
from schemas import ContextualSentence, SelectedContent, SelectionOutput, State
from utils import get_llm, get_ollama, voting


async def single_selection_attempt(
    contextual_sentence: ContextualSentence, llm_instance: BaseChatModel
) -> Tuple[bool, Optional[str]]:
    prompt_template = ChatPromptTemplate(
        [
            ("system", SELECTION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    prompt_messages = prompt_template.invoke(
        {
            "excerpt": contextual_sentence.context,
            "sentence": contextual_sentence.sentence,
        }
    )

    selection_response: SelectionOutput = llm_instance.with_structured_output(
        SelectionOutput
    ).invoke(prompt_messages)

    if (
        not selection_response
        or not selection_response.processed_sentence
        or selection_response.no_verifiable_claims
    ):
        return False, None
    if selection_response.remains_unchanged:
        processed_sentence = contextual_sentence.sentence
    else:
        processed_sentence = selection_response.processed_sentence.strip()
    return True, processed_sentence


def create_selected_content(
    processed_sentence: str, contextual_sentence: ContextualSentence
) -> SelectedContent:
    return SelectedContent(
        processed_sentence=processed_sentence,
        original_context_item=contextual_sentence,
    )


async def selector_node(state: State) -> Dict[str, List[SelectedContent]]:
    """Node function to select verifiable sentences from contextual sentences."""
    # Get the contextual sentences from the state
    contextual_sentences = state.contextual_sentences

    # Get LLM instance
    # llm_instance = get_llm(1)
    llm_instance = get_ollama(1)

    # Run the selection process using voting (reduced to single completion for rate limiting)
    selected_results = await voting(
        items=contextual_sentences,
        single_attempt_function=single_selection_attempt,
        llm_instance=llm_instance,
        num_completions=1,
        min_successes=1,
        result_factory=create_selected_content,
        description="Selecting sentences from a text that are verifiable claims.",
    )

    return {"selected_contents": selected_results}
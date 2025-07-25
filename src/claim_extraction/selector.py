from typing import Dict, List, Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

from .prompts import HUMAN_PROMPT, SELECTION_SYSTEM_PROMPT
from .schemas import (
    BatchSelectionOutput,
    ContextualSentence,
    SelectedContent,
    State,
)
from .utils import batch_voting, format_excerpt_sentence_pairs, get_llm

import yaml

def load_config(path=".\config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

async def single_selection_attempt(
    contextual_sentences: List[ContextualSentence], llm_instance: BaseChatModel
) -> Tuple[List[bool], List[Optional[str]]]:
    prompt_template = ChatPromptTemplate(
        [
            ("system", SELECTION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    prompt_messages = prompt_template.invoke(
        {
            "excerpt_sentence_pairs": format_excerpt_sentence_pairs(
                [cs.context for cs in contextual_sentences],
                [cs.sentence for cs in contextual_sentences],
            )
        }
    )

    batch_selection_response: BatchSelectionOutput = llm_instance.with_structured_output(
        BatchSelectionOutput
    ).invoke(prompt_messages)
    if not batch_selection_response or not batch_selection_response.selected_contents:
        return [False], [None]

    flags: List[bool] = []
    extracted_sentences: List[Optional[str]] = []
    selected_contents = batch_selection_response.selected_contents
    for i in range(len(selected_contents)):
        if (
            not selected_contents[i].processed_sentence
            or selected_contents[i].no_verifiable_claims
        ):
            flags.append(False)
            extracted_sentences.append(None)
        else:
            if selected_contents[i].remains_unchanged:
                processed_sentence = contextual_sentences[i].sentence
            else:
                processed_sentence = selected_contents[i].processed_sentence.strip()
            flags.append(True)
            extracted_sentences.append(processed_sentence)
    return flags, extracted_sentences


def create_selected_content(
    processed_sentence: str, contextual_sentence: ContextualSentence
) -> SelectedContent:
    return SelectedContent(
        processed_sentence=processed_sentence,
        original_context_item=contextual_sentence,
    )


def create_batch_selected_content(
    processed_sentences: List[str], contextual_sentences: List[ContextualSentence]
) -> List[SelectedContent]:
    return [
        SelectedContent(
            processed_sentence=processed_sentence, original_context_item=contextual_sentence
        )
        for processed_sentence, contextual_sentence in zip(
            processed_sentences, contextual_sentences
        )
    ]


async def selector_node(state: State) -> Dict[str, List[SelectedContent]]:
    """Node function to select verifiable sentences from contextual sentences."""
    # Get the contextual sentences from the state
    contextual_sentences = state.contextual_sentences

    # Get LLM instance
    llm_instance = get_llm(1)
    # llm_instance = get_ollama(1)

    # Run the selection process using voting (reduced to single completion for rate limiting)
    selected_results = await batch_voting(
        items=contextual_sentences,
        single_attempt_function=single_selection_attempt,
        llm_instance=llm_instance,
        num_completions= config["fact_extraction"]["selection"]["num_completions"],
        min_successes= config["fact_extraction"]["selection"]["min_successes"],
        result_factory=create_batch_selected_content,
        description="contextual sentence",
        batch_size= config["fact_extraction"]["selection"]["batch_size"]
    )

    return {"selected_contents": selected_results}

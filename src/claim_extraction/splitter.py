from typing import Dict, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
import nltk

from .prompts import (
    PUNCTUATION_HUMAN_PROMPT,
    PUNCTUATION_SYSTEM_PROMPT,
    SENTENCE_SPLITTING_SYSTEM_PROMPT,
    SENTENCE_SPLITTING_HUMAN_PROMPT,
)
from .schemas import ContextualSentence, PunctuadedText, SentenceSplittingOutput, State
from .utils import get_llm, load_config

config = load_config()


def get_tokenizer():
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)
        logger.info("Downloading NLTK punkt tokenizer data.")


def Punctuation_LLM(transcript: str, llm_instance: BaseChatModel) -> PunctuadedText:
    """Use LLM to punctuate and split transcript into sentences."""
    prompt_template = ChatPromptTemplate(
        [
            ("system", PUNCTUATION_SYSTEM_PROMPT),
            ("human", PUNCTUATION_HUMAN_PROMPT),
        ]
    )
    try:
        response = llm_instance.with_structured_output(PunctuadedText).invoke(
            prompt_template.invoke({"transcript": transcript})
        )
        return response

    except Exception as e:
        logger.error(" Error communicating with LLM: {}", str(e))
        return [transcript]


def LLM_sentence_splitter(
    punctuated_text: str,
    llm_instance: BaseChatModel,
    preceding_sentences: int = 5,
    following_sentences: int = 5,
) -> SentenceSplittingOutput:
    """Use LLM to split text into sentences with context preservation."""
    prompt_template = ChatPromptTemplate(
        [
            ("system", SENTENCE_SPLITTING_SYSTEM_PROMPT),
            ("human", SENTENCE_SPLITTING_HUMAN_PROMPT),
        ]
    )
    try:
        response = llm_instance.with_structured_output(SentenceSplittingOutput).invoke(
            prompt_template.invoke(
                {
                    "punctuated_text": punctuated_text,
                    "preceding_sentences": preceding_sentences,
                    "following_sentences": following_sentences,
                }
            )
        )
        return response
    except Exception as e:
        logger.error("Error communicating with LLM for sentence splitting: {}", str(e))
        # Fallback to empty result
        return SentenceSplittingOutput(contextual_sentences=[])


async def sentence_splitter(
    llm_instance: BaseChatModel,
    answer_text: str,
    preceding_sentences: int = 5,
    following_sentences: int = 5,
) -> List[ContextualSentence]:
    """
    Splits the answer text into sentences using LLM and returns a list of ContextualSentence objects.

    Args:
        llm_instance: The language model instance to use
        answer_text (str): The text to be split into sentences.
        preceding_sentences (int): Number of sentences before current sentence.
        following_sentences (int): Number of sentences after current sentence.

    Returns:
        List[ContextualSentence]: A list of ContextualSentence objects.
    """
    # First, punctuate the text using LLM
    punctuated_answer_text = Punctuation_LLM(answer_text, llm_instance).text

    # Then, split into sentences with context preservation using LLM
    splitting_result = LLM_sentence_splitter(
        punctuated_text=punctuated_answer_text,
        llm_instance=llm_instance,
        preceding_sentences=preceding_sentences,
        following_sentences=following_sentences,
    )

    return splitting_result.contextual_sentences


async def sentence_splitter_node(state: State) -> Dict[str, List[ContextualSentence]]:
    """Node function to split text into sentences with context."""
    # get the model
    # llm_instance = get_ollama(0)
    llm_instance = get_llm(0)

    # Get the answer text from the state
    answer_text = state.answer_text
    # Split the text into sentences
    contextual_sentences = await sentence_splitter(
        llm_instance=llm_instance,
        answer_text=answer_text,
        preceding_sentences=config["fact_extraction"]["Splitting"]["preceding_sentences"],
        following_sentences=config["fact_extraction"]["Splitting"]["following_sentences"],
    )

    return {"contextual_sentences": contextual_sentences}

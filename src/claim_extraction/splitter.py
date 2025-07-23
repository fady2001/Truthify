from typing import Dict, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
import nltk
from .prompts import PUNCTUATION_HUMAN_PROMPT, PUNCTUATION_SYSTEM_PROMPT
from .schemas import ContextualSentence, PunctuadedText, State
from .utils import get_llm


def get_tokenizer():
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)
        logger.info("Downloading NLTK punkt tokenizer data.")

def Punctuation_LLM(transcript: str, llm_instance:BaseChatModel) -> PunctuadedText:
    """Use LLM to punctuate and split transcript into sentences."""
    prompt_template = ChatPromptTemplate(
        [
            ("system", PUNCTUATION_SYSTEM_PROMPT),
            ("human", PUNCTUATION_HUMAN_PROMPT),
        ]
    )
    try:
        response = llm_instance.with_structured_output(PunctuadedText).invoke(prompt_template.invoke({"transcript": transcript}))
        # Clean triple backticks if present
        # if raw_output.startswith("") and raw_output.endswith(""):
        #     raw_output = "\n".join(raw_output.split("\n")[1:-1]).strip()
        return response

    except Exception as e:
        logger.error(" Error communicating with LLM: {}", str(e))
        return [transcript]

async def sentence_splitter(
    llm_instance: BaseChatModel,
    answer_text: str,
    preceding_sentences: int = 5,
    following_sentences: int = 5,
) -> List[ContextualSentence]:
    """
    Splits the answer text into sentences and returns a list of ContextualSentence objects.

    Args:
        answer_text (str): The text to be split into sentences.
        preceding_sentences (int): Number of sentences before current sentence.
        following_sentences (int): Number of sentences after current sentence.

    Returns:
        List[ContextualSentence]: A list of ContextualSentence objects.
    """
    # punctuation
    punctuaded_answer_text = Punctuation_LLM(answer_text,llm_instance).text
    
    from nltk.tokenize import sent_tokenize

    # Ensure the tokenizer is downloaded
    get_tokenizer()

    # split by paragraphs and strip whitespace
    paragraphs = [paragraph.strip() for paragraph in punctuaded_answer_text.split("\n") if paragraph.strip()]
    tokenized_sentences = [sent_tokenize(paragraph) for paragraph in paragraphs]
    # Flatten the list of lists into a single list of sentences
    flattened_sentences = [sentence for sublist in tokenized_sentences for sentence in sublist]
    # merge small sentence with the next one if it is too short
    merged_sentences = []
    sentence_index = 0
    while sentence_index < len(flattened_sentences):
        current_sentence = flattened_sentences[sentence_index]
        # Check if the current sentence is too short
        while len(current_sentence) < 10 and sentence_index < len(flattened_sentences) - 1:
            # Merge with the next sentence
            sentence_index += 1
            next_sentence = flattened_sentences[sentence_index]
            current_sentence += " " + next_sentence
        merged_sentences.append(current_sentence.strip())
        sentence_index += 1
    # create ContextualSentence objects
    contextual_sentences = []
    for sentence_idx, sentence in enumerate(merged_sentences):
        start_index = max(0, sentence_idx - preceding_sentences)
        end_index = min(len(merged_sentences), sentence_idx + following_sentences + 1)
        context_parts = []
        # add preceding sentences
        if start_index < sentence_idx:
            context_parts.append("\n[Preceding Sentences:]")
            context_parts.extend(merged_sentences[start_index:sentence_idx])

        # add current sentence
        current_sentence = f"\n[Sentence of Interest for current task:]\n{sentence.strip()}"
        context_parts.append(current_sentence)
        # add following sentences
        if end_index > sentence_idx + 1:
            context_parts.append("\n[Following Sentences:]")
            context_parts.extend(merged_sentences[sentence_idx + 1 : end_index])

        # create context
        context = "\n".join(context_parts) if context_parts else "No context available."
        # create ContextualSentence object
        contextual_sentences.append(
            ContextualSentence(
                sentence=sentence.strip(),
                context=context,
                index=sentence_idx,
            )
        )
    return contextual_sentences


async def sentence_splitter_node(state: State) -> Dict[str, List[ContextualSentence]]:
    """Node function to split text into sentences with context."""
    # get the model
    # llm_instance = get_ollama(0)
    llm_instance = get_llm(0)
    
    # Get the answer text from the state
    answer_text = state.answer_text
    # Split the text into sentences
    contextual_sentences = await sentence_splitter(
        llm_instance = llm_instance,
        answer_text= answer_text,
        preceding_sentences=5,
        following_sentences=5,
    )

    return {"contextual_sentences": contextual_sentences}
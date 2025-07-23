from typing import List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from prompts import PUNCTUATION_HUMAN_PROMPT, PUNCTUATION_SYSTEM_PROMPT
from schemas import PunctuadedText
from utils import get_ollama


def Punctuation_LLM(transcript: str) -> PunctuadedText:
    """Use LLM to punctuate and split transcript into sentences."""
    llm:BaseChatModel = get_ollama()
    prompt_template = ChatPromptTemplate(
        [
            ("system", PUNCTUATION_SYSTEM_PROMPT),
            ("human", PUNCTUATION_HUMAN_PROMPT),
        ]
    )

    try:
        response = llm.with_structured_output(PunctuadedText).invoke(prompt_template.invoke({"transcript": transcript}))

        # Clean triple backticks if present
        # if raw_output.startswith("") and raw_output.endswith(""):
        #     raw_output = "\n".join(raw_output.split("\n")[1:-1]).strip()

        return response

    except Exception as e:
        logger.error(" Error communicating with LLM: {}", str(e))
        return [transcript]
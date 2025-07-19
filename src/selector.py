import asyncio
from typing import Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

from prompts import HUMAN_PROMPT, SELECTION_SYSTEM_PROMPT
from schemas import ContextualSentence, SelectedContent, SelectionOutput
from utils import get_llm, voting


async def single_selection_attempt(context: ContextualSentence, llm_instance:BaseChatModel)-> Tuple[bool, Optional[str]]:
    messages = ChatPromptTemplate(
        [
            ("system", SELECTION_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    prompt_messages = messages.invoke(
        {
            "excerpt": context.context,
            "sentence": context.sentence,
        }
    )

    response:SelectionOutput = llm_instance.with_structured_output(SelectionOutput).invoke(prompt_messages)
    
    if (
        not response
        or not response.processed_sentence
        or response.no_verifiable_claims
    ):
        return False, None
    if response.remains_unchanged:
        processed = context.sentence
    else:
        processed = response.processed_sentence.strip()
    return True, processed
        
def create_selected_content(processed_sentence: str, context: ContextualSentence) -> SelectedContent:
    return SelectedContent(
        processed_sentence=processed_sentence,
        original_context_item=context,
    )


async def main():
    llm = get_llm(1)

    text = (
        "The Earth revolves around the Sun. "
        "Water boils at 100 degrees Celsius. "
        "The Moon is made of cheese."
    )

    from splitter import sentence_splitter
    sentences = sentence_splitter(text)
    # Properly run the async voting function
    result = await voting(
        items=sentences,
        single_attempt_function=single_selection_attempt,
        llm=llm,
        completions=1,
        min_successes=1,
        result_factory=create_selected_content,
        description="Selecting sentences from a text that are verifiable claims."
    )

    for item in result:
        print(item)

if __name__ == "__main__":
    asyncio.run(main())
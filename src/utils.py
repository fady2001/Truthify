import asyncio
import os
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger


def get_llm(num_completions: int = 1):
    from dotenv import load_dotenv

    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    temperature = 0
    if num_completions > 1:
        temperature = 0.2
    llm_instance = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", temperature=temperature, google_api_key=GEMINI_API_KEY
    )
    return llm_instance


T = TypeVar("T")
R = TypeVar("R")


async def voting(
    items: List[T],
    single_attempt_function: Callable[[T, Any], Tuple[bool, Optional[R]]],
    llm_instance: Any,
    num_completions: int,
    min_successes: int,
    result_factory: Callable[[R, T], Any],
    description: str = "item",
) -> List[Any]:
    """Process items with multiple LLM attempts and consensus voting.

    Args:
        items: Items to be passed to the LLM
        single_attempt_function: Function that makes a call to the LLM
        llm_instance: LLM instance
        num_completions: How many attempts per item
        min_successes: How many must succeed
        result_factory: Function to create final result
        description: Item type for logs

    Returns:
        List of successfully processed results
    """
    results = []

    for item in items:
        # Make multiple attempts
        attempts = await asyncio.gather(
            *[single_attempt_function(item, llm_instance) for _ in range(num_completions)]
        )

        # Count successes
        success_count = sum(1 for success, _ in attempts if success)
        # Only proceed if we have enough successes
        if success_count < min_successes:
            logger.info(
                f"Not enough successes ({success_count}/{min_successes}) for {description}"
            )
            continue

        # Use the first successful result
        for success, result in attempts:
            if success and result is not None:
                processed_result = result_factory(result, item)
                if processed_result:
                    results.append(processed_result)
                    break

    return results

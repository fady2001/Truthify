import asyncio
import os
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from loguru import logger


def format_excerpt_sentence_pairs(excerpts: List[str], sentences: List[str]) -> str:
    """
    Format lists of excerpts and sentences into the structured format expected by prompts.
    
    Args:
        excerpts: List of text excerpts
        sentences: List of sentences corresponding to each excerpt
        
    Returns:
        Formatted string with numbered pairs
        
    Raises:
        ValueError: If excerpts and sentences lists have different lengths
    """
    if len(excerpts) != len(sentences):
        raise ValueError(f"Excerpts ({len(excerpts)}) and sentences ({len(sentences)}) must have the same length")
    
    formatted_pairs = []
    
    for i, (excerpt, sentence) in enumerate(zip(excerpts, sentences), 1):
        pair_text = f"""Pair {i}:
Excerpt: "{excerpt}"
Sentence: "{sentence}" """
        formatted_pairs.append(pair_text)
    
    return "\n\n".join(formatted_pairs)

def get_llm(num_completions: int = 1):
    from dotenv import load_dotenv

    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    temperature = 0
    if num_completions > 1:
        temperature = 0.2
    llm_instance = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", temperature=temperature, google_api_key=GEMINI_API_KEY
    )
    return llm_instance

def get_ollama(num_completions: int = 1):
    temperature = 0
    if num_completions > 1:
        temperature = 0.2
    llm_instance = ChatOllama(
        model="gemma3:1b",  # or llama3, mistral, etc.
        base_url="http://localhost:11434",  # optional if default
        temperature=temperature,
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
        # attempts = await asyncio.gather(
        #     *[single_attempt_function(item, llm_instance) for _ in range(num_completions)]
        # )
        request_delay = 5  # seconds
        # Make attempts sequentially with delay to respect rate limits
        attempts = []
        for i in range(num_completions):
            try:
                attempt = await single_attempt_function(item, llm_instance)
                attempts.append(attempt)
                
                # Add delay between requests (except for the last one)
                if i < num_completions - 1:
                    await asyncio.sleep(request_delay)
            except Exception as e:
                logger.warning(f"Request failed for {description}: {e}")
                attempts.append((False, None))
                
                # If we hit a rate limit, wait longer
                if "429" in str(e) or "quota" in str(e).lower():
                    logger.info("Rate limit hit, waiting 60 seconds...")
                    await asyncio.sleep(60)

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


T = TypeVar("T")
R = TypeVar("R")
async def batch_voting(
    items: List[T],
    single_attempt_function: Callable[[List[T], Any], Tuple[List[bool], List[Optional[R]]]],
    llm_instance: Any,
    num_completions: int,
    min_successes: int,
    result_factory: Callable[[List[R], List[T]], Any],
    description: str = "item",
    batch_size: int = 5,
) -> List[Any]:
    """Process items with multiple LLM attempts and consensus voting using batch requests.

    Args:
        items: Items to be passed to the LLM
        single_attempt_function: Function that makes a call to the LLM
        llm_instance: LLM instance
        num_completions: How many attempts per item
        min_successes: How many must succeed
        result_factory: Function to create final result
        description: Item type for logs
        batch_size: Number of items to process in parallel per batch

    Returns:
        List of successfully processed results
    """
    # Process items in batches
    for batch_start in range(0, len(items), batch_size):
        batch_end = min(batch_start + batch_size, len(items))
        batch_items = items[batch_start:batch_end]
        
        logger.info(f"Processing batch {batch_start//batch_size + 1} with {len(batch_items)} {description}s")
        
        # Process each item in the batch with multiple attempts
        for attempt_num in range(num_completions):
            try:
                flags, processed_batch = await single_attempt_function(batch_items, llm_instance)
            except Exception as e:
                logger.warning(f"Request failed for {description} (attempt {attempt_num + 1}): {e}")                
                # If we hit a rate limit, wait longer
                if "429" in str(e) or "quota" in str(e).lower():
                    logger.info("Rate limit hit, waiting 60 seconds...")
                    await asyncio.sleep(60)
                elif "503" in str(e) or "timeout" in str(e).lower():
                    logger.info("Service unavailable or timeout, waiting 30 seconds...")
                    await asyncio.sleep(30)
            
            # Evaluate this item's attempts
            success_count = sum(1 for success, _ in item_attempts if success)
            
            if success_count >= min_successes:
                # Use the first successful result
                for success, result in item_attempts:
                    if success and result is not None:
                        processed_result = result_factory(result, item)
                        if processed_result:
                            batch_results.append(processed_result)
                            break
            else:
                logger.info(
                    f"Not enough successes ({success_count}/{min_successes}) for {description}"
                )
        
        results.extend(batch_results)
        
        # Add delay between batches (except for the last one)
        if batch_end < len(items):
            logger.info(f"Waiting {batch_delay} seconds before next batch...")
            await asyncio.sleep(batch_delay)
    
    logger.info(f"Completed processing {len(items)} {description}s, got {len(results)} successful results")
    return results

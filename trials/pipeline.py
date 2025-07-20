import asyncio
from typing import List

from loguru import logger

from decomposition import decomposition_stage
from disambiguator import create_disambiguated_content, single_disambiguation_attempt
from schemas import PotentialClaim
from selector import create_selected_content, single_selection_attempt
from splitter import sentence_splitter
from utils import get_llm, voting


class TruthifyPipeline:
    """Complete pipeline for processing text through all stages: splitting → selection → disambiguation → decomposition."""

    def __init__(self, num_completions: int = 3, min_successes: int = 2):
        """Initialize the pipeline.

        Args:
            num_completions: Number of LLM attempts per stage
            min_successes: Minimum successful attempts required
        """
        self.num_completions = num_completions
        self.min_successes = min_successes
        self.llm_instance = get_llm(1)

    async def run_pipeline(
        self, text: str, preceding_sentences: int = 5, following_sentences: int = 5
    ) -> List[PotentialClaim]:
        """Run the complete pipeline on input text.

        Args:
            text: Input text to process
            preceding_sentences: Number of sentences before current sentence for context
            following_sentences: Number of sentences after current sentence for context

        Returns:
            List of potential claims extracted from the text
        """
        logger.info("Starting Truthify pipeline")
        logger.info(f"Input text length: {len(text)} characters")

        # Stage 1: Splitting
        logger.info("Stage 1: Splitting text into sentences")
        contextual_sentences = sentence_splitter(
            text, preceding_sentences=preceding_sentences, following_sentences=following_sentences
        )
        logger.info(f"Split into {len(contextual_sentences)} sentences")

        if not contextual_sentences:
            logger.warning("No sentences found after splitting")
            return []

        # Stage 2: Selection
        logger.info("Stage 2: Selecting sentences with verifiable claims")
        selected_items = await voting(
            items=contextual_sentences,
            single_attempt_function=single_selection_attempt,
            llm_instance=self.llm_instance,
            num_completions=self.num_completions,
            min_successes=self.min_successes,
            result_factory=create_selected_content,
            description="sentences with verifiable claims",
        )
        logger.info(f"Selected {len(selected_items)} sentences with verifiable claims")

        if not selected_items:
            logger.warning("No sentences selected for further processing")
            return []

        # Stage 3: Disambiguation
        logger.info("Stage 3: Disambiguating selected sentences")
        disambiguated_items = await voting(
            items=selected_items,
            single_attempt_function=single_disambiguation_attempt,
            llm_instance=self.llm_instance,
            num_completions=self.num_completions,
            min_successes=self.min_successes,
            result_factory=create_disambiguated_content,
            description="disambiguated sentences",
        )
        logger.info(f"Disambiguated {len(disambiguated_items)} sentences")

        if not disambiguated_items:
            logger.warning("No sentences successfully disambiguated")
            return []

        # Stage 4: Decomposition
        logger.info("Stage 4: Decomposing sentences into atomic claims")
        all_potential_claims = []

        for disambiguated_item in disambiguated_items:
            claims = await decomposition_stage(disambiguated_item)
            all_potential_claims.extend(claims)

        logger.info(f"Extracted {len(all_potential_claims)} potential claims total")
        logger.info("Pipeline completed successfully")

        return all_potential_claims

    def print_pipeline_summary(self, potential_claims: List[PotentialClaim]):
        """Print a summary of the pipeline results.

        Args:
            potential_claims: List of potential claims from the pipeline
        """
        if not potential_claims:
            logger.info("No claims were extracted from the input text")
            return

        logger.info(f"\n{'=' * 60}")
        logger.info("PIPELINE RESULTS SUMMARY")
        logger.info(f"{'=' * 60}")
        logger.info(f"Total claims extracted: {len(potential_claims)}")

        # Group claims by original sentence
        claims_by_sentence = {}
        for claim in potential_claims:
            original_idx = claim.original_index
            if original_idx not in claims_by_sentence:
                claims_by_sentence[original_idx] = {
                    "original_sentence": claim.original_sentence,
                    "disambiguated_sentence": claim.disambiguated_sentence,
                    "claims": [],
                }
            claims_by_sentence[original_idx]["claims"].append(claim.claim_text)

        for idx, sentence_data in claims_by_sentence.items():
            logger.info(f"\nSentence {idx + 1}:")
            logger.info(f"  Original: {sentence_data['original_sentence']}")
            logger.info(f"  Disambiguated: {sentence_data['disambiguated_sentence']}")
            logger.info(f"  Claims ({len(sentence_data['claims'])}):")
            for i, claim in enumerate(sentence_data["claims"], 1):
                logger.info(f"    {i}. {claim}")


async def run_truthify_pipeline(
    text: str,
    num_completions: int = 3,
    min_successes: int = 2,
    preceding_sentences: int = 5,
    following_sentences: int = 5,
) -> List[PotentialClaim]:
    """Convenience function to run the complete pipeline.

    Args:
        text: Input text to process
        num_completions: Number of LLM attempts per stage
        min_successes: Minimum successful attempts required
        preceding_sentences: Number of sentences before current sentence for context
        following_sentences: Number of sentences after current sentence for context

    Returns:
        List of potential claims extracted from the text
    """
    pipeline = TruthifyPipeline(num_completions, min_successes)
    potential_claims = await pipeline.run_pipeline(text, preceding_sentences, following_sentences)
    pipeline.print_pipeline_summary(potential_claims)
    return potential_claims


async def main():
    """Example usage of the pipeline."""
    sample_text = """
    Climate change is one of the most pressing issues of our time. The Earth's average temperature has risen by 1.1 degrees Celsius since the late 1800s. 
    
    Scientists around the world agree that human activities are the primary cause of this warming. Carbon dioxide levels in the atmosphere have increased by over 40% since pre-industrial times.
    
    Many countries have committed to reducing their greenhouse gas emissions. The Paris Agreement, signed in 2015, aims to limit global warming to well below 2 degrees Celsius.
    
    Renewable energy sources like solar and wind power are becoming more affordable and efficient. Solar panel costs have decreased by 90% over the past decade.
    
    However, we need to act faster to avoid the worst impacts of climate change. Some experts warn that we have less than a decade to make significant changes to our energy systems.
    """

    logger.info("Running example pipeline with sample climate text")
    potential_claims = await run_truthify_pipeline(
        text=sample_text,
        num_completions=1,  # Using 1 for faster demo
        min_successes=1,
        preceding_sentences=3,
        following_sentences=3,
    )

    if potential_claims:
        logger.info(
            f"\nExtracted {len(potential_claims)} potential claims ready for fact-checking!"
        )
    else:
        logger.warning("No claims were extracted from the sample text")


if __name__ == "__main__":
    asyncio.run(main())

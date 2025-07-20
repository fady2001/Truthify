import asyncio
import time
from typing import List

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from loguru import logger

from decomposition import decomposition_node
from disambiguator import disambiguator_node
from schemas import PotentialClaim, State
from selector import selector_node
from splitter import sentence_splitter_node


class TruthifyLangGraphPipeline:
    """LangGraph-based pipeline for processing text through all truthify stages."""

    def __init__(self):
        """Initialize the LangGraph pipeline."""
        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph:
        """Build the LangGraph workflow using the unified State schema."""
        workflow = StateGraph(State)

        # Add nodes for each stage using our node functions
        workflow.add_node("sentence_splitter", self._wrap_node(sentence_splitter_node))
        workflow.add_node("selector", self._wrap_node(selector_node))
        workflow.add_node("disambiguator", self._wrap_node(disambiguator_node))
        workflow.add_node("decomposition", self._wrap_node(decomposition_node))

        # Add edges to connect the nodes sequentially
        workflow.add_edge(START, "sentence_splitter")

        # Add conditional edges to handle empty results at each stage
        workflow.add_conditional_edges(
            "sentence_splitter",
            self._check_contextual_sentences,
            {"continue": "selector", "end": END},
        )
        workflow.add_conditional_edges(
            "selector", self._check_selected_contents, {"continue": "disambiguator", "end": END}
        )
        workflow.add_conditional_edges(
            "disambiguator",
            self._check_disambiguated_contents,
            {"continue": "decomposition", "end": END},
        )
        workflow.add_edge("decomposition", END)

        return workflow.compile()

    def _wrap_node(self, node_func):
        """Wrap node functions with error handling and timing."""

        async def wrapped_node(state: dict) -> dict:
            start_time = time.time()
            node_name = node_func.__name__.replace("_node", "")

            logger.info(f"Starting {node_name} stage")

            try:
                # Convert dict to State object for the node function
                # Use model_validate for slightly better performance
                state_obj = State.model_validate(state)

                # Call the node function
                result = await node_func(state_obj)

                # Return the result dict directly (no need to update original state)
                processing_time = time.time() - start_time
                logger.info(f"Completed {node_name} stage in {processing_time:.2f}s")

                return result

            except Exception as e:
                error_msg = f"Error in {node_name} stage: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg) from e

        return wrapped_node

    def _check_contextual_sentences(self, state: State) -> str:
        """Check if sentence splitting produced results."""
        if not state.contextual_sentences or len(state.contextual_sentences) == 0:
            logger.warning("No sentences found after splitting, ending pipeline")
            return "end"
        logger.info(f"Found {len(state.contextual_sentences)} contextual sentences")
        return "continue"

    def _check_selected_contents(self, state: State) -> str:
        """Check if selection stage produced results."""
        if not state.selected_contents or len(state.selected_contents) == 0:
            logger.warning("No sentences selected for further processing, ending pipeline")
            return "end"
        logger.info(f"Selected {len(state.selected_contents)} sentences with verifiable content")
        return "continue"

    def _check_disambiguated_contents(self, state: State) -> str:
        """Check if disambiguation stage produced results."""
        if not state.disambiguated_contents or len(state.disambiguated_contents) == 0:
            logger.warning("No sentences successfully disambiguated, ending pipeline")
            return "end"
        logger.info(f"Disambiguated {len(state.disambiguated_contents)} sentences")
        return "continue"

    async def run_pipeline(self, answer_text: str) -> State:
        """Run the complete pipeline using LangGraph.

        Args:
            answer_text: Input text to process

        Returns:
            Final state with all processing results
        """
        # Create initial state
        initial_state = State(answer_text=answer_text)

        logger.info(f"Starting LangGraph pipeline with text length: {len(answer_text)} characters")
        start_time = time.time()

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        total_time = time.time() - start_time
        logger.info(f"Pipeline completed in {total_time:.2f} seconds")

        return final_state

    def print_pipeline_summary(self, final_state: State):
        """Print a comprehensive summary of the pipeline results."""
        logger.info(f"\n{'=' * 60}")
        logger.info("LANGGRAPH PIPELINE RESULTS SUMMARY")
        logger.info(f"{'=' * 60}")

        # Stage-by-stage summary
        logger.info("Processing Results:")
        logger.info(f"  Contextual Sentences: {len(final_state['contextual_sentences'])}")
        logger.info(f"  Selected Contents: {len(final_state['selected_contents'])}")
        logger.info(f"  Disambiguated Contents: {len(final_state['disambiguated_contents'])}")
        logger.info(f"  Potential Claims: {len(final_state['potential_claims'])}")

        if not final_state['potential_claims']:
            logger.info("No claims were extracted from the input text")
            return

        # Group claims by original sentence
        claims_by_sentence = {}
        for claim in final_state['potential_claims']:
            original_idx = claim.original_index
            if original_idx not in claims_by_sentence:
                claims_by_sentence[original_idx] = {
                    "original_sentence": claim.original_sentence,
                    "disambiguated_sentence": claim.disambiguated_sentence,
                    "claims": [],
                }
            claims_by_sentence[original_idx]["claims"].append(claim.claim_text)

        logger.info("\nExtracted Claims by Sentence:")
        for idx, sentence_data in claims_by_sentence.items():
            logger.info(f"\nSentence {idx + 1}:")
            logger.info(f"  Original: {sentence_data['original_sentence']}")
            if sentence_data["disambiguated_sentence"] != sentence_data["original_sentence"]:
                logger.info(f"  Disambiguated: {sentence_data['disambiguated_sentence']}")
            logger.info(f"  Claims ({len(sentence_data['claims'])}):")
            for i, claim in enumerate(sentence_data["claims"], 1):
                logger.info(f"    {i}. {claim}")


async def run_truthify_pipeline(answer_text: str) -> List[PotentialClaim]:
    """Convenience function to run the LangGraph Truthify pipeline.

    Args:
        answer_text: Input text to process

    Returns:
        List of potential claims extracted from the text
    """
    pipeline = TruthifyLangGraphPipeline()
    final_state = await pipeline.run_pipeline(answer_text)
    pipeline.print_pipeline_summary(final_state)
    return final_state['potential_claims']


async def main():
    """Example usage of the LangGraph Truthify pipeline."""
    sample_text = """
    the radius of the Earth is approximately 6,371 kilometers. This value can vary slightly depending on where you measure it due to the Earth's equatorial bulge.
    """

    logger.info("Running LangGraph Truthify Pipeline Demo")

    try:
        potential_claims = await run_truthify_pipeline(sample_text)

        if potential_claims:
            logger.info(f"\n✅ Successfully extracted {len(potential_claims)} potential claims!")
            logger.info("These claims are now ready for fact-checking verification.")
        else:
            logger.warning("❌ No claims were extracted from the input text")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env file
    asyncio.run(main())

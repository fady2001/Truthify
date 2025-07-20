import asyncio
from typing import List, Dict, Any, Optional, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph import StateGraph, END, START
from loguru import logger

from decomposition import decomposition_stage
from disambiguator import single_disambiguation_attempt, create_disambiguated_content
from schemas import PotentialClaim, ContextualSentence, SelectedContent, DisambiguatedContent
from selector import single_selection_attempt, create_selected_content
from splitter import sentence_splitter
from utils import get_llm, voting


class PipelineState(TypedDict):
    """State for the LangGraph pipeline."""

    # Input
    text: str
    preceding_sentences: int
    following_sentences: int
    num_completions: int
    min_successes: int

    # Intermediate results
    contextual_sentences: Optional[List[ContextualSentence]]
    selected_items: Optional[List[SelectedContent]]
    disambiguated_items: Optional[List[DisambiguatedContent]]

    # Final output
    potential_claims: Optional[List[PotentialClaim]]

    # Metadata
    stage_results: Dict[str, Any]
    errors: List[str]
    processing_time: Dict[str, float]


class LangGraphTruthifyPipeline:
    """LangGraph-based pipeline for processing text through all stages."""

    def __init__(self):
        """Initialize the LangGraph pipeline."""
        self.llm_instance = None
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(PipelineState)

        # Add nodes for each stage
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("split", self._split_node)
        workflow.add_node("select", self._select_node)
        workflow.add_node("disambiguate", self._disambiguate_node)
        workflow.add_node("decompose", self._decompose_node)
        workflow.add_node("finalize", self._finalize_node)

        # Add edges to connect the nodes
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "split")
        workflow.add_conditional_edges(
            "split", self._check_split_results, {"continue": "select", "end": "finalize"}
        )
        workflow.add_conditional_edges(
            "select", self._check_select_results, {"continue": "disambiguate", "end": "finalize"}
        )
        workflow.add_conditional_edges(
            "disambiguate",
            self._check_disambiguate_results,
            {"continue": "decompose", "end": "finalize"},
        )
        workflow.add_edge("decompose", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    async def _initialize_node(
        self, state: PipelineState, config: RunnableConfig
    ) -> PipelineState:
        """Initialize the pipeline state and LLM instance."""
        logger.info("Initializing LangGraph Truthify pipeline")
        logger.info(f"Input text length: {len(state['text'])} characters")

        # Initialize LLM instance
        self.llm_instance = get_llm(1)

        # Initialize state tracking
        state["stage_results"] = {}
        state["errors"] = []
        state["processing_time"] = {}

        return state

    async def _split_node(self, state: PipelineState, config: RunnableConfig) -> PipelineState:
        """Stage 1: Split text into sentences."""
        import time

        start_time = time.time()

        logger.info("Stage 1: Splitting text into sentences")

        try:
            contextual_sentences = sentence_splitter(
                state["text"],
                preceding_sentences=state.get("preceding_sentences", 5),
                following_sentences=state.get("following_sentences", 5),
            )

            state["contextual_sentences"] = contextual_sentences
            state["stage_results"]["split"] = {
                "sentences_count": len(contextual_sentences),
                "success": True,
            }

            logger.info(f"Split into {len(contextual_sentences)} sentences")

        except Exception as e:
            error_msg = f"Error in split stage: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["contextual_sentences"] = []
            state["stage_results"]["split"] = {"success": False, "error": error_msg}

        state["processing_time"]["split"] = time.time() - start_time
        return state

    async def _select_node(self, state: PipelineState, config: RunnableConfig) -> PipelineState:
        """Stage 2: Select sentences with verifiable claims."""
        import time

        start_time = time.time()

        logger.info("Stage 2: Selecting sentences with verifiable claims")

        try:
            selected_items = await voting(
                items=state["contextual_sentences"],
                single_attempt_function=single_selection_attempt,
                llm_instance=self.llm_instance,
                num_completions=state.get("num_completions", 3),
                min_successes=state.get("min_successes", 2),
                result_factory=create_selected_content,
                description="sentences with verifiable claims",
            )

            state["selected_items"] = selected_items
            state["stage_results"]["select"] = {
                "selected_count": len(selected_items),
                "success": True,
            }

            logger.info(f"Selected {len(selected_items)} sentences with verifiable claims")

        except Exception as e:
            error_msg = f"Error in select stage: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["selected_items"] = []
            state["stage_results"]["select"] = {"success": False, "error": error_msg}

        state["processing_time"]["select"] = time.time() - start_time
        return state

    async def _disambiguate_node(
        self, state: PipelineState, config: RunnableConfig
    ) -> PipelineState:
        """Stage 3: Disambiguate selected sentences."""
        import time

        start_time = time.time()

        logger.info("Stage 3: Disambiguating selected sentences")

        try:
            disambiguated_items = await voting(
                items=state["selected_items"],
                single_attempt_function=single_disambiguation_attempt,
                llm_instance=self.llm_instance,
                num_completions=state.get("num_completions", 3),
                min_successes=state.get("min_successes", 2),
                result_factory=create_disambiguated_content,
                description="disambiguated sentences",
            )

            state["disambiguated_items"] = disambiguated_items
            state["stage_results"]["disambiguate"] = {
                "disambiguated_count": len(disambiguated_items),
                "success": True,
            }

            logger.info(f"Disambiguated {len(disambiguated_items)} sentences")

        except Exception as e:
            error_msg = f"Error in disambiguate stage: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["disambiguated_items"] = []
            state["stage_results"]["disambiguate"] = {"success": False, "error": error_msg}

        state["processing_time"]["disambiguate"] = time.time() - start_time
        return state

    async def _decompose_node(self, state: PipelineState, config: RunnableConfig) -> PipelineState:
        """Stage 4: Decompose sentences into atomic claims."""
        import time

        start_time = time.time()

        logger.info("Stage 4: Decomposing sentences into atomic claims")

        try:
            all_potential_claims = []

            for disambiguated_item in state["disambiguated_items"]:
                claims = await decomposition_stage(disambiguated_item)
                all_potential_claims.extend(claims)

            state["potential_claims"] = all_potential_claims
            state["stage_results"]["decompose"] = {
                "claims_count": len(all_potential_claims),
                "success": True,
            }

            logger.info(f"Extracted {len(all_potential_claims)} potential claims total")

        except Exception as e:
            error_msg = f"Error in decompose stage: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["potential_claims"] = []
            state["stage_results"]["decompose"] = {"success": False, "error": error_msg}

        state["processing_time"]["decompose"] = time.time() - start_time
        return state

    async def _finalize_node(self, state: PipelineState, config: RunnableConfig) -> PipelineState:
        """Finalize the pipeline and log results."""
        logger.info("Pipeline completed")

        # Log processing times
        total_time = sum(state["processing_time"].values())
        logger.info(f"Total processing time: {total_time:.2f} seconds")
        for stage, time_taken in state["processing_time"].items():
            percentage = (time_taken / total_time) * 100 if total_time > 0 else 0
            logger.info(f"  {stage}: {time_taken:.2f}s ({percentage:.1f}%)")

        # Log any errors
        if state["errors"]:
            logger.warning(f"Pipeline completed with {len(state['errors'])} errors:")
            for error in state["errors"]:
                logger.warning(f"  - {error}")

        return state

    def _check_split_results(self, state: PipelineState) -> str:
        """Check if split stage produced results."""
        if not state.get("contextual_sentences") or len(state["contextual_sentences"]) == 0:
            logger.warning("No sentences found after splitting, ending pipeline")
            return "end"
        return "continue"

    def _check_select_results(self, state: PipelineState) -> str:
        """Check if select stage produced results."""
        if not state.get("selected_items") or len(state["selected_items"]) == 0:
            logger.warning("No sentences selected for further processing, ending pipeline")
            return "end"
        return "continue"

    def _check_disambiguate_results(self, state: PipelineState) -> str:
        """Check if disambiguate stage produced results."""
        if not state.get("disambiguated_items") or len(state["disambiguated_items"]) == 0:
            logger.warning("No sentences successfully disambiguated, ending pipeline")
            return "end"
        return "continue"

    async def run_pipeline(
        self,
        text: str,
        num_completions: int = 3,
        min_successes: int = 2,
        preceding_sentences: int = 5,
        following_sentences: int = 5,
    ) -> Dict[str, Any]:
        """Run the complete pipeline using LangGraph.

        Args:
            text: Input text to process
            num_completions: Number of LLM attempts per stage
            min_successes: Minimum successful attempts required
            preceding_sentences: Number of sentences before current sentence for context
            following_sentences: Number of sentences after current sentence for context

        Returns:
            Complete pipeline state with results
        """
        initial_state: PipelineState = {
            "text": text,
            "preceding_sentences": preceding_sentences,
            "following_sentences": following_sentences,
            "num_completions": num_completions,
            "min_successes": min_successes,
            "contextual_sentences": None,
            "selected_items": None,
            "disambiguated_items": None,
            "potential_claims": None,
            "stage_results": {},
            "errors": [],
            "processing_time": {},
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        return final_state

    def print_pipeline_summary(self, final_state: Dict[str, Any]):
        """Print a comprehensive summary of the pipeline results."""
        potential_claims = final_state.get("potential_claims", [])

        logger.info(f"\n{'=' * 60}")
        logger.info("LANGGRAPH PIPELINE RESULTS SUMMARY")
        logger.info(f"{'=' * 60}")

        # Stage-by-stage summary
        logger.info("Stage Results:")
        for stage, results in final_state.get("stage_results", {}).items():
            status = "✅ SUCCESS" if results.get("success") else "❌ FAILED"
            logger.info(f"  {stage.upper()}: {status}")
            if stage == "split" and results.get("success"):
                logger.info(f"    - Sentences: {results.get('sentences_count', 0)}")
            elif stage == "select" and results.get("success"):
                logger.info(f"    - Selected: {results.get('selected_count', 0)}")
            elif stage == "disambiguate" and results.get("success"):
                logger.info(f"    - Disambiguated: {results.get('disambiguated_count', 0)}")
            elif stage == "decompose" and results.get("success"):
                logger.info(f"    - Claims: {results.get('claims_count', 0)}")

        if not potential_claims:
            logger.info("No claims were extracted from the input text")
            return

        logger.info(f"\nTotal claims extracted: {len(potential_claims)}")

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

        logger.info("\nDetailed Results:")
        for idx, sentence_data in claims_by_sentence.items():
            logger.info(f"\nSentence {idx + 1}:")
            logger.info(f"  Original: {sentence_data['original_sentence']}")
            logger.info(f"  Disambiguated: {sentence_data['disambiguated_sentence']}")
            logger.info(f"  Claims ({len(sentence_data['claims'])}):")
            for i, claim in enumerate(sentence_data["claims"], 1):
                logger.info(f"    {i}. {claim}")


async def run_langgraph_pipeline(
    text: str,
    num_completions: int = 3,
    min_successes: int = 2,
    preceding_sentences: int = 5,
    following_sentences: int = 5,
) -> List[PotentialClaim]:
    """Convenience function to run the LangGraph pipeline.

    Args:
        text: Input text to process
        num_completions: Number of LLM attempts per stage
        min_successes: Minimum successful attempts required
        preceding_sentences: Number of sentences before current sentence for context
        following_sentences: Number of sentences after current sentence for context

    Returns:
        List of potential claims extracted from the text
    """
    pipeline = LangGraphTruthifyPipeline()
    final_state = await pipeline.run_pipeline(
        text, num_completions, min_successes, preceding_sentences, following_sentences
    )
    pipeline.print_pipeline_summary(final_state)
    return final_state.get("potential_claims", [])


async def main():
    """Example usage of the LangGraph pipeline."""
    sample_text = """
    Artificial intelligence is transforming healthcare. Machine learning algorithms can now diagnose certain cancers with 95% accuracy.
    
    Google's DeepMind developed AlphaFold, which solved the protein folding problem. This breakthrough could accelerate drug discovery by decades.
    
    However, AI in healthcare raises privacy concerns. Patient data must be protected while enabling medical breakthroughs.
    
    The FDA has approved over 100 AI-based medical devices since 2020. These tools are helping doctors make faster and more accurate diagnoses.
    """

    logger.info("Running LangGraph pipeline with sample AI healthcare text")
    potential_claims = await run_langgraph_pipeline(
        text=sample_text,
        num_completions=1,  # Using 1 for faster demo
        min_successes=1,
        preceding_sentences=2,
        following_sentences=2,
    )

    if potential_claims:
        logger.info(
            f"\nExtracted {len(potential_claims)} potential claims ready for fact-checking!"
        )
    else:
        logger.warning("No claims were extracted from the sample text")


if __name__ == "__main__":
    asyncio.run(main())

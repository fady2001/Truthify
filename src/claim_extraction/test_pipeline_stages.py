import asyncio
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict

from .decomposition import decomposition_node
from .disambiguator import disambiguator_node
from loguru import logger
from .schemas import State
from .selector import selector_node
from .splitter import sentence_splitter_node
from .utils import get_llm


class PipelineStagesTester:
    """Test each stage of the Truthify pipeline individually and log outputs."""

    def __init__(self, output_dir: str = "pipeline_test_outputs"):
        """Initialize the tester with an output directory for logs."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create timestamped subdirectory for this test run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_run_dir = self.output_dir / f"test_run_{timestamp}"
        self.test_run_dir.mkdir(exist_ok=True)

        logger.info(f"Test outputs will be saved to: {self.test_run_dir}")

    def save_stage_output(self, stage_name: str, data: Any, stage_input: Any = None) -> None:
        """Save stage output to a JSON file."""
        output_file = self.test_run_dir / f"{stage_name}_output.json"

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage_name,
            "input_summary": self._summarize_input(stage_input) if stage_input else None,
            "output": self._serialize_for_json(data),
            "output_summary": self._summarize_output(stage_name, data),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {stage_name} output to {output_file}")

    def _serialize_for_json(self, obj: Any) -> Any:
        """Convert Pydantic models and other objects to JSON-serializable format."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        else:
            return obj

    def _summarize_input(self, stage_input: Any) -> Dict[str, Any]:
        """Create a summary of stage input."""
        if hasattr(stage_input, "answer_text"):
            return {
                "type": "State",
                "answer_text_length": len(stage_input.answer_text),
                "answer_text_preview": stage_input.answer_text[:200] + "..."
                if len(stage_input.answer_text) > 200
                else stage_input.answer_text,
                "contextual_sentences_count": len(stage_input.contextual_sentences)
                if hasattr(stage_input, "contextual_sentences")
                else 0,
                "selected_contents_count": len(stage_input.selected_contents)
                if hasattr(stage_input, "selected_contents")
                else 0,
                "disambiguated_contents_count": len(stage_input.disambiguated_contents)
                if hasattr(stage_input, "disambiguated_contents")
                else 0,
                "potential_claims_count": len(stage_input.potential_claims)
                if hasattr(stage_input, "potential_claims")
                else 0,
            }
        return {"type": type(stage_input).__name__, "value": str(stage_input)[:200]}

    def _summarize_output(self, stage_name: str, data: Any) -> Dict[str, Any]:
        """Create a summary of stage output."""
        if isinstance(data, dict):
            summary = {"type": "dict", "keys": list(data.keys())}

            # Add specific summaries based on stage
            if stage_name == "sentence_splitter" and "contextual_sentences" in data:
                summary["contextual_sentences_count"] = len(data["contextual_sentences"])
                if data["contextual_sentences"]:
                    summary["sample_sentence"] = (
                        data["contextual_sentences"][0].sentence[:100] + "..."
                    )

            elif stage_name == "selector" and "selected_contents" in data:
                summary["selected_contents_count"] = len(data["selected_contents"])
                if data["selected_contents"]:
                    summary["sample_processed_sentence"] = (
                        data["selected_contents"][0].processed_sentence[:100] + "..."
                    )

            elif stage_name == "disambiguator" and "disambiguated_contents" in data:
                summary["disambiguated_contents_count"] = len(data["disambiguated_contents"])
                if data["disambiguated_contents"]:
                    summary["sample_disambiguated_sentence"] = (
                        data["disambiguated_contents"][0].disambiguated_sentence[:100] + "..."
                    )

            elif stage_name == "decomposition" and "potential_claims" in data:
                summary["potential_claims_count"] = len(data["potential_claims"])
                if data["potential_claims"]:
                    summary["sample_claim"] = data["potential_claims"][0].claim_text[:100] + "..."

            return summary

        return {
            "type": type(data).__name__,
            "length": len(data) if hasattr(data, "__len__") else "N/A",
        }

    async def test_sentence_splitter_stage(self, input_text: str) -> State:
        """Test the sentence splitter stage."""
        logger.info("Testing sentence splitter stage...")

        # Create initial state
        initial_state = State(answer_text=input_text)

        try:
            # Run sentence splitter
            result = await sentence_splitter_node(initial_state)

            # Update state with results
            updated_state = State(
                answer_text=input_text, contextual_sentences=result["contextual_sentences"]
            )

            # Save output
            self.save_stage_output("sentence_splitter", result, initial_state)

            # Log detailed results
            logger.info(
                f"Sentence splitter produced {len(result['contextual_sentences'])} contextual sentences"
            )
            for i, cs in enumerate(result["contextual_sentences"][:3]):  # Show first 3
                logger.info(f"  Sentence {i + 1}: {cs.sentence[:100]}...")

            return updated_state

        except Exception as e:
            logger.error(f"Error in sentence splitter stage: {e}")
            raise

    async def test_selector_stage(self, state: State) -> State:
        """Test the selector stage."""
        logger.info("Testing selector stage...")

        try:
            # Run selector
            result = await selector_node(state)

            # Update state with results
            updated_state = State(
                answer_text=state.answer_text,
                contextual_sentences=state.contextual_sentences,
                selected_contents=result["selected_contents"],
            )

            # Save output
            self.save_stage_output("selector", result, state)

            # Log detailed results
            logger.info(f"Selector produced {len(result['selected_contents'])} selected contents")
            for i, sc in enumerate(result["selected_contents"][:3]):  # Show first 3
                logger.info(f"  Selected {i + 1}: {sc.processed_sentence[:100]}...")

            return updated_state

        except Exception as e:
            logger.error(f"Error in selector stage: {e}")
            raise

    async def test_disambiguator_stage(self, state: State) -> State:
        """Test the disambiguator stage."""
        logger.info("Testing disambiguator stage...")

        try:
            # Run disambiguator
            result = await disambiguator_node(state)

            # Update state with results
            updated_state = State(
                answer_text=state.answer_text,
                contextual_sentences=state.contextual_sentences,
                selected_contents=state.selected_contents,
                disambiguated_contents=result["disambiguated_contents"],
            )

            # Save output
            self.save_stage_output("disambiguator", result, state)

            # Log detailed results
            logger.info(
                f"Disambiguator produced {len(result['disambiguated_contents'])} disambiguated contents"
            )
            for i, dc in enumerate(result["disambiguated_contents"][:3]):  # Show first 3
                logger.info(f"  Disambiguated {i + 1}: {dc.disambiguated_sentence[:100]}...")

            return updated_state

        except Exception as e:
            logger.error(f"Error in disambiguator stage: {e}")
            raise

    async def test_decomposition_stage(self, state: State) -> State:
        """Test the decomposition stage."""
        logger.info("Testing decomposition stage...")

        try:
            # Run decomposition
            result = await decomposition_node(state)

            # Update state with results
            updated_state = State(
                answer_text=state.answer_text,
                contextual_sentences=state.contextual_sentences,
                selected_contents=state.selected_contents,
                disambiguated_contents=state.disambiguated_contents,
                potential_claims=result["potential_claims"],
            )

            # Save output
            self.save_stage_output("decomposition", result, state)

            # Log detailed results
            logger.info(
                f"Decomposition produced {len(result['potential_claims'])} potential claims"
            )
            for i, claim in enumerate(result["potential_claims"][:5]):  # Show first 5
                logger.info(f"  Claim {i + 1}: {claim.claim_text[:100]}...")

            return updated_state

        except Exception as e:
            logger.error(f"Error in decomposition stage: {e}")
            raise

    async def run_full_stage_by_stage_test(self, input_text: str) -> State:
        """Run all stages sequentially and log each stage's output."""
        logger.info("=" * 80)
        logger.info("STARTING FULL STAGE-BY-STAGE PIPELINE TEST")
        logger.info("=" * 80)

        # Save input text
        input_file = self.test_run_dir / "input_text.txt"
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(input_text)
        logger.info(f"Input text saved to {input_file}")

        try:
            # Stage 1: Sentence Splitter
            state = await self.test_sentence_splitter_stage(input_text)

            # Check if we have results to continue
            if not state.contextual_sentences:
                logger.warning("No contextual sentences produced. Stopping pipeline.")
                return state

            # Stage 2: Selector
            state = await self.test_selector_stage(state)

            # Check if we have results to continue
            if not state.selected_contents:
                logger.warning("No selected contents produced. Stopping pipeline.")
                return state

            # Stage 3: Disambiguator
            state = await self.test_disambiguator_stage(state)

            # Check if we have results to continue
            if not state.disambiguated_contents:
                logger.warning("No disambiguated contents produced. Stopping pipeline.")
                return state

            # Stage 4: Decomposition
            state = await self.test_decomposition_stage(state)

            # Save final state
            self.save_stage_output("final_state", state)

            # Generate summary report
            self._generate_summary_report(state)

            logger.info("=" * 80)
            logger.info("STAGE-BY-STAGE PIPELINE TEST COMPLETED")
            logger.info("=" * 80)

            return state

        except Exception as e:
            logger.error(f"Pipeline test failed: {e}")
            raise

    def _generate_summary_report(self, final_state: State) -> None:
        """Generate a comprehensive summary report."""
        report_file = self.test_run_dir / "summary_report.txt"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("TRUTHIFY PIPELINE STAGE-BY-STAGE TEST SUMMARY\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Test Run Directory: {self.test_run_dir}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

            # Input summary
            f.write("INPUT TEXT:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Length: {len(final_state.answer_text)} characters\n")
            f.write(f"Preview: {final_state.answer_text[:300]}...\n\n")

            # Stage results summary
            f.write("STAGE RESULTS:\n")
            f.write("-" * 20 + "\n")
            f.write(
                f"1. Sentence Splitter: {len(final_state.contextual_sentences)} contextual sentences\n"
            )
            f.write(f"2. Selector: {len(final_state.selected_contents)} selected contents\n")
            f.write(
                f"3. Disambiguator: {len(final_state.disambiguated_contents)} disambiguated contents\n"
            )
            f.write(f"4. Decomposition: {len(final_state.potential_claims)} potential claims\n\n")

            # Detailed results
            if final_state.potential_claims:
                f.write("FINAL CLAIMS:\n")
                f.write("-" * 20 + "\n")
                for i, claim in enumerate(final_state.potential_claims, 1):
                    f.write(f"{i}. {claim.claim_text}\n")
            else:
                f.write("NO CLAIMS EXTRACTED\n")

        logger.info(f"Summary report saved to {report_file}")


async def main():
    """Main function to test the pipeline with various sample texts."""

    # Sample texts for testing
    test_texts = [
        """
اكتشف العلماء أن الأرض مسطحة بشكل جزئي، وهذا ما يفسر سبب ظهور الأفق مستويًا عند النظر إليه من الأماكن المرتفعة. ويُعتقد أن هذا الشكل المسطح يجعل الجاذبية تتوزع بشكل غير متساوٍ في مناطق مختلفة من الكوكب. كما أن الإنسان لا يمكنه العيش أكثر من 100 سنة، فالجسم البشري يتوقف تمامًا عن تجديد الخلايا بعد سن السبعين. أما بالنسبة للقمر، فقد هبطت عليه أول بعثة بشرية في عام 1969، وتوقفت رحلات ناسا إليه بعد أن تبين أنه لا يحتوي على أي موارد مفيدة.

ويُقال إن الشمس عبارة عن كرة نارية صلبة تدور حول الأرض، وهذا ما تؤكده بعض النظريات الحديثة التي تعيد النظر في نموذج مركزية الشمس. من ناحية أخرى، يُعد الماء مركبًا بسيطًا يتكون من ذرتي هيدروجين وذرة أكسجين، وهو يغطي حوالي 71% من سطح الأرض

        """
    ]

    from dotenv import load_dotenv

    load_dotenv()

    tester = PipelineStagesTester()

    # Test each sample text
    for i, text in enumerate(test_texts, 1):
        logger.info(f"\n{'=' * 20} TESTING SAMPLE TEXT {i} {'=' * 20}")

        try:
            final_state = await tester.run_full_stage_by_stage_test(text.strip())

            logger.info(f"Test {i} completed successfully!")
            logger.info(f"Final claims count: {len(final_state.potential_claims)}")

        except Exception as e:
            logger.error(f"Test {i} failed: {e}")

        # Add delay between tests to respect rate limits
        if i < len(test_texts):
            logger.info("Waiting 10 seconds before next test...")
            await asyncio.sleep(10)

    logger.info(f"\nAll tests completed! Check outputs in: {tester.test_run_dir}")


if __name__ == "__main__":
    asyncio.run(main())

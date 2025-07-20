import asyncio
import time
from typing import Dict, Any

from loguru import logger

from pipeline import run_truthify_pipeline
from langgraph_pipeline import run_langgraph_pipeline


async def compare_pipelines():
    """Compare the basic pipeline vs LangGraph pipeline implementations."""

    sample_text = """
    OpenAI released GPT-4 in March 2023, marking a significant milestone in artificial intelligence development. 
    The model demonstrates improved reasoning capabilities compared to its predecessor GPT-3.5.
    
    Microsoft has invested over $10 billion in OpenAI since 2019. This partnership has enabled the integration 
    of AI technologies into Microsoft's product suite, including Office 365 and Azure cloud services.
    
    However, concerns about AI safety and alignment remain prevalent. Researchers worry about potential 
    misuse of advanced language models for generating misinformation or harmful content.
    
    The European Union is developing comprehensive AI regulation frameworks. The AI Act, proposed in 2021, 
    aims to establish safety standards for high-risk AI applications.
    """

    logger.info("=" * 80)
    logger.info("PIPELINE COMPARISON: Basic vs LangGraph Implementation")
    logger.info("=" * 80)

    # Test parameters
    test_params = {
        "num_completions": 1,
        "min_successes": 1,
        "preceding_sentences": 3,
        "following_sentences": 3,
    }

    # Run Basic Pipeline
    logger.info("\n🔸 RUNNING BASIC PIPELINE...")
    start_time = time.time()

    try:
        basic_claims = await run_truthify_pipeline(text=sample_text, **test_params)
        basic_time = time.time() - start_time
        basic_success = True
        logger.info(f"✅ Basic pipeline completed in {basic_time:.2f}s")

    except Exception as e:
        basic_claims = []
        basic_time = time.time() - start_time
        basic_success = False
        logger.error(f"❌ Basic pipeline failed: {str(e)}")

    logger.info("\n" + "=" * 60)

    # Run LangGraph Pipeline
    logger.info("\n🔸 RUNNING LANGGRAPH PIPELINE...")
    start_time = time.time()

    try:
        langgraph_claims = await run_langgraph_pipeline(text=sample_text, **test_params)
        langgraph_time = time.time() - start_time
        langgraph_success = True
        logger.info(f"✅ LangGraph pipeline completed in {langgraph_time:.2f}s")

    except Exception as e:
        langgraph_claims = []
        langgraph_time = time.time() - start_time
        langgraph_success = False
        logger.error(f"❌ LangGraph pipeline failed: {str(e)}")

    # Comparison Summary
    logger.info("\n" + "=" * 80)
    logger.info("COMPARISON SUMMARY")
    logger.info("=" * 80)

    logger.info(f"📊 PERFORMANCE:")
    logger.info(
        f"  Basic Pipeline:     {basic_time:.2f}s | {len(basic_claims) if basic_success else 0} claims"
    )
    logger.info(
        f"  LangGraph Pipeline: {langgraph_time:.2f}s | {len(langgraph_claims) if langgraph_success else 0} claims"
    )

    if basic_success and langgraph_success:
        time_diff = abs(basic_time - langgraph_time)
        faster = "Basic" if basic_time < langgraph_time else "LangGraph"
        logger.info(f"  Winner: {faster} (faster by {time_diff:.2f}s)")

        claims_diff = abs(len(basic_claims) - len(langgraph_claims))
        if claims_diff == 0:
            logger.info(f"  Both pipelines extracted the same number of claims!")
        else:
            more_claims = "Basic" if len(basic_claims) > len(langgraph_claims) else "LangGraph"
            logger.info(f"  {more_claims} extracted {claims_diff} more claims")

    logger.info(f"\n🎯 KEY DIFFERENCES:")
    logger.info(f"  Basic Pipeline:")
    logger.info(f"    ✓ Simpler implementation")
    logger.info(f"    ✓ Direct sequential execution")
    logger.info(f"    ✓ Lightweight and fast")
    logger.info(f"    ✓ Easy to understand and modify")

    logger.info(f"  LangGraph Pipeline:")
    logger.info(f"    ✓ State management and persistence")
    logger.info(f"    ✓ Conditional routing and early exit")
    logger.info(f"    ✓ Detailed error tracking per stage")
    logger.info(f"    ✓ Performance timing per stage")
    logger.info(f"    ✓ Graph-based workflow visualization")
    logger.info(f"    ✓ Better suited for complex workflows")


def print_architecture_comparison():
    """Print detailed architecture comparison."""

    logger.info("\n" + "=" * 80)
    logger.info("ARCHITECTURE COMPARISON")
    logger.info("=" * 80)

    logger.info("\n🏗️  BASIC PIPELINE ARCHITECTURE:")
    logger.info("   Input Text")
    logger.info("       ↓")
    logger.info("   [Splitter] → contextual_sentences")
    logger.info("       ↓")
    logger.info("   [Selector] → selected_items")
    logger.info("       ↓")
    logger.info("   [Disambiguator] → disambiguated_items")
    logger.info("       ↓")
    logger.info("   [Decomposer] → potential_claims")
    logger.info("       ↓")
    logger.info("   Output Claims")

    logger.info("\n🕸️  LANGGRAPH PIPELINE ARCHITECTURE:")
    logger.info("   Input Text")
    logger.info("       ↓")
    logger.info("   [Initialize] → Setup state & LLM")
    logger.info("       ↓")
    logger.info("   [Split] → Check results → Continue/End")
    logger.info("       ↓                         ↓")
    logger.info("   [Select] → Check results → Continue/End")
    logger.info("       ↓                         ↓")
    logger.info("   [Disambiguate] → Check results → Continue/End")
    logger.info("       ↓                         ↓")
    logger.info("   [Decompose] → → → → → → → → → ↓")
    logger.info("       ↓                         ↓")
    logger.info("   [Finalize] ← ← ← ← ← ← ← ← ← ←")
    logger.info("       ↓")
    logger.info("   Output Claims + Metadata")

    logger.info("\n🎯 USE CASE RECOMMENDATIONS:")
    logger.info("   📝 Choose BASIC PIPELINE when:")
    logger.info("     • You need simple, fast processing")
    logger.info("     • Workflow is straightforward")
    logger.info("     • Minimal error handling required")
    logger.info("     • Prototyping and experimentation")

    logger.info("   🌐 Choose LANGGRAPH PIPELINE when:")
    logger.info("     • You need robust state management")
    logger.info("     • Complex conditional workflows")
    logger.info("     • Detailed monitoring and debugging")
    logger.info("     • Production environments")
    logger.info("     • Integration with other LangGraph components")


async def main():
    """Run the pipeline comparison."""
    print_architecture_comparison()
    await compare_pipelines()

    logger.info("\n" + "=" * 80)
    logger.info("✨ COMPARISON COMPLETE!")
    logger.info("Both pipelines are ready for your fact-checking workflow!")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

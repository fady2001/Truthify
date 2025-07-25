import logging
import time
from typing import List

from api_schemas import ClaimResult, FactCheckResponse, TextInput
from fastapi import FastAPI, HTTPException
import yaml

from claim_checking.agent_search import verify_claim_with_variants
from claim_checking.claim_similarity import filter_rephrasings_by_similarity
from claim_checking.rephraser import rephrase_claim_v2
from claim_extraction.langgraph_pipeline import run_truthify_pipeline
from claim_extraction.schemas import PotentialClaim
from src.get_text import extract_from_url_withtimestamps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load configuration
def load_config(path="./config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()

# Create FastAPI app
app = FastAPI(
    title="Truthify API",
    description="An API for extracting and fact-checking claims from text",
    version="1.0.0",
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Truthify API is running", "status": "healthy"}

@app.post("/youtube-fact-check", response_model=FactCheckResponse)
async def fact_check_youtube(input_data: TextInput):
    """
    Extract claims from YouTube video transcript and perform fact-checking on each claim.
    """
    start_time = time.time()

    try:
        logger.info(f"Starting fact-check for YouTube URL: {input_data.text[:100]}...")

        # Step 1: Extract transcript with timestamps
        transcript_segments, language = extract_from_url_withtimestamps(input_data.text)

        if not transcript_segments:
            return FactCheckResponse(
                input_text=input_data.text,
                extracted_claims=[],
                fact_check_results=[],
                processing_time=time.time() - start_time,
            )

        # Step 2: Extract claims from the transcript segments
        claims: List[PotentialClaim] = await run_truthify_pipeline(
            " ".join(segment['text'] for segment in transcript_segments)
        )
        extracted_claims = [claim.claim_text for claim in claims]

        if not extracted_claims:
            return FactCheckResponse(
                input_text=input_data.text,
                extracted_claims=[],
                fact_check_results=[],
                processing_time=time.time() - start_time,
            )

        logger.info(f"Extracted {len(extracted_claims)} claims")

        # Step 3: Rephrase claims for better search
        rephrased_outputs = rephrase_claim_v2(
            extracted_claims,
            language=config["fact_checking"]["Search"]["language"],
            n_variants=config["fact_checking"]["rephrasing"]["n_variants"],
        )

        # Step 4: Filter rephrasings by similarity
        rephrased_lists = [entry["rephrased"] for entry in rephrased_outputs]
        filtered_results = filter_rephrasings_by_similarity(
            claims=[entry["original"] for entry in rephrased_outputs],
            rephrasings=rephrased_lists,
            threshold=config["fact_checking"]["check_similarity"]["threshold"],
            top_k=config["fact_checking"]["check_similarity"]["top_k"],
        )

        # Step 5: Fact-check each claim
        fact_check_results = []
        for entry in filtered_results:
            original = entry["original"]
            variants = entry["selected_variants"]

            logger.info(f"Fact-checking claim: {original}")

            # Verify the claim with its variants
            final_decision = verify_claim_with_variants(
                original, language=config["fact_checking"]["Search"]["language"], variants=variants
            )

            # Format the result
            claim_result = ClaimResult(
                claim=final_decision["claim"],
                status=final_decision["status"],
                explanation=final_decision["explanation"],
                sources=final_decision.get("sources", []),
            )
            fact_check_results.append(claim_result)
            # Add delay to avoid rate limiting
            time.sleep(30)
        processing_time = time.time() - start_time
        logger.info(f"Completed fact-checking in {processing_time:.2f}s")
        return FactCheckResponse(
            input_text=input_data.text,
            extracted_claims=extracted_claims,
            fact_check_results=fact_check_results,
            processing_time=processing_time,
        )
    except Exception as e:
        logger.error(f"Error in fact-checking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in fact-checking: {str(e)}")

@app.post("/text-fact-check", response_model=FactCheckResponse)
async def fact_check_text(input_data: TextInput):
    """
    Extract claims from text and perform fact-checking on each claim.
    This is the full pipeline including rephrasing, similarity filtering, and verification.
    """
    start_time = time.time()

    try:
        logger.info(f"Starting fact-check for text: {input_data.text[:100]}...")

        # Step 1: Extract claims
        claims: List[PotentialClaim] = await run_truthify_pipeline(input_data.text)
        extracted_claims = [claim.claim_text for claim in claims]

        if not extracted_claims:
            return FactCheckResponse(
                input_text=input_data.text,
                extracted_claims=[],
                fact_check_results=[],
                processing_time=time.time() - start_time,
            )

        logger.info(f"Extracted {len(extracted_claims)} claims")

        # Step 2: Rephrase claims for better search
        rephrased_outputs = rephrase_claim_v2(
            extracted_claims,
            language=config["fact_checking"]["Search"]["language"],
            n_variants=config["fact_checking"]["rephrasing"]["n_variants"],
        )

        # Step 3: Filter rephrasings by similarity
        rephrased_lists = [entry["rephrased"] for entry in rephrased_outputs]
        filtered_results = filter_rephrasings_by_similarity(
            claims=[entry["original"] for entry in rephrased_outputs],
            rephrasings=rephrased_lists,
            threshold=config["fact_checking"]["check_similarity"]["threshold"],
            top_k=config["fact_checking"]["check_similarity"]["top_k"],
        )

        # Step 4: Fact-check each claim
        fact_check_results = []
        for entry in filtered_results:
            original = entry["original"]
            variants = entry["selected_variants"]

            logger.info(f"Fact-checking claim: {original}")

            # Verify the claim with its variants
            final_decision = verify_claim_with_variants(
                original, language=config["fact_checking"]["Search"]["language"], variants=variants
            )

            # Format the result
            claim_result = ClaimResult(
                claim=final_decision["claim"],
                status=final_decision["status"],
                explanation=final_decision["explanation"],
                sources=final_decision.get("sources", []),
            )

            fact_check_results.append(claim_result)

            # Add delay to avoid rate limiting
            time.sleep(30)

        processing_time = time.time() - start_time

        logger.info(f"Completed fact-checking in {processing_time:.2f}s")

        return FactCheckResponse(
            input_text=input_data.text,
            extracted_claims=extracted_claims,
            fact_check_results=fact_check_results,
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Error in fact-checking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in fact-checking: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Truthify API",
        "version": "1.0.0",
        "endpoints": {
            "fact_check": "/text-fact-check",
            "youtube_fact_check": "/youtube-fact-check",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

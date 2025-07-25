import os
from typing import List

import cohere
from dotenv import load_dotenv
import yaml


def load_config(path=".\config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
client = cohere.Client(COHERE_API_KEY)

def rephrase_claim_v2(claims: List[str], language: str, n_variants: int = 5) -> List[str]:
    rephrased_results = []

    for claim in claims:
        prompt = (
        f"You are a professional rewriter specialized in factual claims.\n\n"
        f"Your task is to generate {n_variants} distinct, clear, fluent, and natural-sounding rephrasings of the following factual claim in {language}.\n\n"
        "Guidelines:\n"
        "- Preserve the **exact factual meaning**. Do not add, omit, or alter any facts.\n"
        "- Use **grammatically correct**, fluent, and **formal** language.\n"
        "- Avoid vague, ambiguous, or informal expressions.\n"
        "- Each variant must use a **different structure, vocabulary, or phrasing**.\n"
        "- Eliminate redundancy and improve clarity without over-simplifying.\n"
        "- Use **transition words or connectors** if they enhance flow or readability.\n"
        "- Keep rephrasings concise, but complete — no fragments.\n"
        "- Output only the rephrased sentences — no comments, explanations, or extra formatting.\n"
        f"- All outputs must be in **{language}**.\n\n"
        f"Original Claim ({language}): \"{claim}\"\n\n"
        "Rephrased Variants:\n"
    )


        response = client.generate(
            model=config["fact_checking"]["rephrasing"]["llm"]["model"],
            prompt=prompt,
            temperature=config["fact_checking"]["rephrasing"]["llm"]["temperature"],
            max_tokens=config["fact_checking"]["rephrasing"]["llm"]["max_tokens"],
            stop_sequences=["--"]
        )

        raw_text = response.generations[0].text.strip()
        lines = raw_text.split("\n")

        # Clean and collect the top `n_variants` non-empty lines
        cleaned_variants = []
        for line in lines:
            line = line.strip().lstrip("-•0123456789. ").strip('" ')
            if line:
                cleaned_variants.append(line)
            if len(cleaned_variants) == n_variants:
                break

        rephrased_results.append({
            "original": claim,
            "rephrased": cleaned_variants
        })

    return rephrased_results

import os
from typing import Dict, List

from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import GoogleSearchAPIWrapper, WikipediaAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2 
)

google_tool = Tool(
    name="Google Search",
    func=GoogleSearchAPIWrapper().run,
    description="Useful for real-time or web-based information"
)

wiki_tool = Tool(
    name="Wikipedia",
    func=WikipediaAPIWrapper(max_results=4).run,
    description="Useful for factual, encyclopedic knowledge"
)

tavily_tool = Tool(
    name="Tavily Search",   
    func= TavilySearchResults(max_results=3).run ,
    description="Useful for searching the web with Tavily"  
)

agent = initialize_agent(
    tools=[tavily_tool, wiki_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True ,
    handle_parsing_errors=True ,
    max_iterations=2
)


def build_single_variant_prompt(variant: str, language: str) -> str:
    prompt = (
    f"You are a professional fact-checking assistant. Your task is to verify the following claim using only the tools 'Tavily Search' and 'Wikipedia'.\n\n"
    f"Respond entirely in this language: **{language}**.\n"
    f"Search, think, and explain in **{language}** only.\n\n"

    "🔹 Process:\n"
    "1. Use ONLY 'Tavily Search' and 'Wikipedia' to collect factual evidence.\n"
    "2. At each step, follow this format:\n"
    "   Action: <Tool Name>\n"
    "   Action Input: <Search Query>\n"
    "   Observation: <Summary of result>\n"
    "   Thought: <Your reasoning>\n"
    "3. Repeat as needed until you're ready to assess the claim.\n\n"

    "🔹 Final Output Format:\n"
    "Final Answer: [True / False / Unverifiable]\n"
    "Explanation: [Brief reasoning based on the evidence you observed]\n"
    "Sources:\n"
    "- [Page Title 1] - [URL 1]\n"
    "- [Page Title 2] - [URL 2]\n"
    "- ...\n\n"

    f"🔹 Claim ({language}): \"{variant}\"\n\n"
    "Begin your fact-checking now:"
    )
    return prompt


def verify_variant_with_agent(variant: str, language: str) -> Dict:
    prompt = build_single_variant_prompt(variant, language)
    response = agent.run(prompt)

    return {
        "variant": variant,
        "agent_response": response
    }


def build_final_decision_prompt(original_claim: str, variant_responses: List[Dict], language: str) -> str:
    joined_variants = "\n\n".join(
        f"Variant: {r['variant']}\nResponse:\n{r['agent_response']}" for r in variant_responses
    )

    final_prompt = (
        f"You are a fact-checking assistant.\n\n"
        f"Your task is to determine the final verdict for the original claim based on multiple verification attempts of reworded variants.\n\n"
        f"Respond entirely in **{language}**.\n\n"
        f"Original Claim: \"{original_claim}\"\n\n"
        f"Variant Verifications:\n\n"
        f"{joined_variants}\n\n"
        "Now, based on all these results, give the final decision about the original claim.\n\n"
        "Respond using this format:\n"
        "Final Answer: [True / False / Unverifiable]\n"
        "Explanation: [Your reasoning combining all the above analyses]\n"
        "Sources:\n"
        "- [Page Title 1] - [URL 1]\n"
        "- [Page Title 2] - [URL 2]\n"
        "- ...\n\n"
    )

    return final_prompt

def extract_sources_from_response(response: str) -> List[Dict[str, str]]:
    sources = []
    for line in response.strip().split("\n"):
        if line.startswith("- "):
            try:
                title, url = line[2:].split(" - ", 1)
                sources.append({"title": title.strip(), "url": url.strip()})
            except ValueError:
                continue
    return sources


def verify_claim_with_variants(original_claim: str, language: str, variants: List):
    results = []
    all_sources = []
    for v in variants:
        result = verify_variant_with_agent(v, language)
        sources = extract_sources_from_response(result["agent_response"])
        result["sources"] = sources
        all_sources.extend(sources)
        results.append(result)

    final_prompt = build_final_decision_prompt(original_claim, results, language)

    final_response = llm.invoke(final_prompt)

    status = ""
    explanation = ""
    final_sources = [] 

    final_response = final_response.content if hasattr(final_response, 'content') else str(final_response)


    for line in final_response.strip().split("\n"):
        if line.startswith("Final Answer:"):
            status = line.replace("Final Answer:", "").strip()
        elif line.startswith("Explanation:"):
            explanation = line.replace("Explanation:", "").strip()
        elif line.startswith("- "):
            try:
                title, url = line[2:].split(" - ", 1)
                final_sources.append({"title": title.strip(), "url": url.strip()})
            except ValueError:
                continue
        if not status:
            first_line = final_response.strip().split("\n")[0].strip()
            if first_line.lower() in ["true", "false", "unverifiable"]:
                status = first_line.capitalize()
    
    return {
        "claim": original_claim,
        "status": status,
        "explanation": explanation,
        "sources": final_sources if final_sources else all_sources,  
    }

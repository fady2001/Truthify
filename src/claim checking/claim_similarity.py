
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")

def filter_rephrasings_by_similarity( claims: List[str], rephrasings: List[List[str]], threshold: float = 0.8, top_k: int = 3 ) -> List[Dict]:

    results = []

    for original, variants in zip(claims, rephrasings):

        sentences = [original] + variants
        embeddings = model.encode(sentences)

        similarities = cosine_similarity([embeddings[0]], embeddings[1:])[0]

        filtered = [
            {"rephrased": variant, "similarity_score": float(sim)}
            for variant, sim in zip(variants, similarities)
            if sim >= threshold
        ]

        filtered = sorted(filtered, key=lambda x: x["similarity_score"], reverse=True)

        if filtered:
            selected_variants = [item["rephrased"] for item in filtered[:top_k]]
        else:
            selected_variants = [original]  

        results.append({
            "original": original,
            "selected_variants": selected_variants
        })

    return results

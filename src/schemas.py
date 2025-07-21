from operator import add
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field


class ContextualSentence(BaseModel):
    sentence: str = Field(description="The sentence to be processed.")
    context: str = Field(description="The context in which the sentence is used.")
    index: int = Field(default=None, description="The index of the sentence in the original text.")
    
    
class SelectionOutput(BaseModel):
    """Response schema for selection LLM calls. used for voting operation"""
    processed_sentence: Optional[str] = Field(
        default=None, description="The processed sentence containing verifiable content"
    )
    no_verifiable_claims: bool = Field(
        description="Flag indicating if no verifiable claims were found"
    )
    remains_unchanged: bool = Field(
        description="Flag indicating if the sentence remains unchanged"
    )
    
class SelectedContent(BaseModel):
    """Content selected as potentially verifiable."""

    processed_sentence: str = Field(
        description="Original or modified verifiable sentence after selection"
    )
    original_context_item: ContextualSentence = Field(
        description="Reference to the original contextual sentence"
    )

class DisambiguationOutput(BaseModel):
    """Response schema for disambiguation LLM calls."""

    disambiguated_sentence: Optional[str] = Field(
        default=None, description="The sentence with ambiguities resolved"
    )
    cannot_be_disambiguated: bool = Field(
        description="Flag indicating if the sentence cannot be disambiguated",
    )
    
class DisambiguatedContent(BaseModel):
    """Content with pronoun references and ambiguities resolved."""

    disambiguated_sentence: str = Field(
        description="Sentence with ambiguities resolved"
    )
    original_selected_item: SelectedContent = Field(
        description="Reference to the original selected content"
    )
    
class DecompositionOutput(BaseModel):
    """Response schema for decomposition LLM calls."""

    claims: List[str] = Field(
        default_factory=list, description="List of extracted factual claims"
    )
    no_claims: bool = Field(
        description="Flag indicating if no verifiable claims were found"
    )
    
class PotentialClaim(BaseModel):
    """A factual claim extracted from disambiguated content."""
    
    claim_text: str = Field(description="Text of the potential claim")
    disambiguated_sentence: str = Field(
        description="The disambiguated sentence the claim was extracted from"
    )
    original_sentence: str = Field(
        description="The original sentence from the answer text"
    )
    original_index: int = Field(
        description="Index of the original sentence in the answer text"
    )
    
class State(BaseModel):
    """The workflow graph state object."""
    answer_text: str = Field(description="The answer text being analyzed")
    contextual_sentences: List[ContextualSentence] = Field(
        default_factory=list, description="Sentences with their surrounding context"
    )
    selected_contents: Annotated[List[SelectedContent], add] = Field(
        default_factory=list, description="Contents selected as potentially verifiable"
    )
    disambiguated_contents: Annotated[List[DisambiguatedContent], add] = Field(
        default_factory=list, description="Contents with ambiguities resolved"
    )
    potential_claims: Annotated[List[PotentialClaim], add] = Field(
        default_factory=list, description="Potential claims extracted from content"
    )
from typing import Optional

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

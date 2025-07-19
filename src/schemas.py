from pydantic import BaseModel, Field


class ContextualSentence(BaseModel):
    sentence: str = Field(description="The sentence to be processed.")
    context: str = Field(description="The context in which the sentence is used.")
    index: int = Field(default=None, description="The index of the sentence in the original text.")
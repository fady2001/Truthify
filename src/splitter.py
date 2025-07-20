from typing import List

from loguru import logger
import nltk

from schemas import ContextualSentence


def get_tokenizer():
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)
        logger.info("Downloading NLTK punkt tokenizer data.")


def sentence_splitter(
    answer_text: str,
    preceding_sentences: int = 5,
    following_sentences: int = 5,
) -> List[ContextualSentence]:
    """
    Splits the answer text into sentences and returns a list of ContextualSentence objects.

    Args:
        answer_text (str): The text to be split into sentences.
        preceding_sentences (int): Number of sentences before current sentence.
        following_sentences (int): Number of sentences after current sentence.

    Returns:
        List[ContextualSentence]: A list of ContextualSentence objects.
    """
    from nltk.tokenize import sent_tokenize

    # Ensure the tokenizer is downloaded
    get_tokenizer()

    # split by paragraphs and strip whitespace
    paragraphs = [paragraph.strip() for paragraph in answer_text.split("\n") if paragraph.strip()]
    tokenized_sentences = [sent_tokenize(paragraph) for paragraph in paragraphs]
    # Flatten the list of lists into a single list of sentences
    flattened_sentences = [sentence for sublist in tokenized_sentences for sentence in sublist]
    # merge small sentence with the next one if it is too short
    merged_sentences = []
    sentence_index = 0
    while sentence_index < len(flattened_sentences):
        current_sentence = flattened_sentences[sentence_index]
        # Check if the current sentence is too short
        while len(current_sentence) < 10 and sentence_index < len(flattened_sentences) - 1:
            # Merge with the next sentence
            sentence_index += 1
            next_sentence = flattened_sentences[sentence_index]
            current_sentence += " " + next_sentence
        merged_sentences.append(current_sentence.strip())
        sentence_index += 1
    # create ContextualSentence objects
    contextual_sentences = []
    for sentence_idx, sentence in enumerate(merged_sentences):
        start_index = max(0, sentence_idx - preceding_sentences)
        end_index = min(len(merged_sentences), sentence_idx + following_sentences + 1)
        context_parts = []
        # add preceding sentences
        if start_index < sentence_idx:
            context_parts.append("\n[Preceding Sentences:]")
            context_parts.extend(merged_sentences[start_index:sentence_idx])

        # add current sentence
        current_sentence = f"\n[Sentence of Interest for current task:]\n{sentence.strip()}"
        context_parts.append(current_sentence)
        # add following sentences
        if end_index > sentence_idx + 1:
            context_parts.append("\n[Following Sentences:]")
            context_parts.extend(merged_sentences[sentence_idx + 1 : end_index])

        # create context
        context = "\n".join(context_parts) if context_parts else "No context available."
        # create ContextualSentence object
        contextual_sentences.append(
            ContextualSentence(
                sentence=sentence.strip(),
                context=context,
                index=sentence_idx,
            )
        )
    return contextual_sentences


if __name__ == "__main__":
    # run a simple test to ensure it works
    sample_text = """
    Hello world! This is a test. Let's see if the tokenizer works.
    
    It should split this text into sentences correctly.
    
    And handle multiple sentences in a paragraph.
    
    Also, it should ignore empty lines and whitespace.
    
    Finally, it should be able to handle short sentences.
    
    This is a short one.
    
    Times'up.
    
    This is a longer sentence that should not be merged with the previous short one.
    
    This is the last sentence in the text.
    
    """
    contextual_sentences = sentence_splitter(
        sample_text, preceding_sentences=2, following_sentences=2
    )
    for idx, contextual_sentence in enumerate(contextual_sentences):
        print(f"\n🔸 Sentence {idx + 1}:")
        print(f"Original: {contextual_sentence.sentence}")
        print(f"Index: {contextual_sentence.index}")
        print(f"Context preview: {contextual_sentence.context}")
        print("-" * 40)

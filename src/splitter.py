from typing import List

from loguru import logger
import nltk

from schemas import ContextualSentence


def get_tokenizer():
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab',quiet=True)
        logger.info("Downloading NLTK punkt tokenizer data.")
        
def sentence_splitter(
    answer_text: str,
    p_sentences: int = 5,
    f_sentences: int = 5,
)-> List[ContextualSentence]:
    """
    Splits the answer text into sentences and returns a list of ContextualSentence objects.

    Args:
        answer_text (str): The text to be split into sentences.
        p_sentences (int): Number of sentences before current sentence.
        f_sentences (int): Number of sentences after current sentence.

    Returns:
        List[ContextualSentence]: A list of ContextualSentence objects.
    """
    from nltk.tokenize import sent_tokenize

    # Ensure the tokenizer is downloaded
    get_tokenizer()

    # split by paragraphs and strip whitespace
    paragraphs = [p.strip() for p in answer_text.split('\n') if p.strip()]
    tokenized_sentences = [sent_tokenize(p) for p in paragraphs]
    # Flatten the list of lists into a single list of sentences
    tokenized_sentences_flatted = [sentence for sublist in tokenized_sentences for sentence in sublist]
    # merge small sentence with the next one if it is too short
    merged_sentences = []
    i=0
    while i < len(tokenized_sentences_flatted):
        current_sentence = tokenized_sentences_flatted[i]
        # Check if the current sentence is too short
        while len(current_sentence) < 10 and i < len(tokenized_sentences_flatted) - 1:
            # Merge with the next sentence
            i += 1
            next_sentence = tokenized_sentences_flatted[i]
            current_sentence += ' ' + next_sentence
        merged_sentences.append(current_sentence.strip())
        i += 1   
    # create ContextualSentence objects
    contextual_sentences = []
    for i, sentence in enumerate(merged_sentences):
        start_index = max(0, i - p_sentences)
        end_index = min(len(merged_sentences), i + f_sentences + 1)
        context_parts = []
        # add preceding sentences
        if start_index < i:
            context_parts.append("\n[Preceding Sentences:]")
            context_parts.extend(merged_sentences[start_index:i])
            
        # add current sentence
        current_sentence = f"\n[Sentence of Interest for current task:]\n{sentence.strip()}"
        context_parts.append(current_sentence)
        # add following sentences
        if end_index > i + 1:
            context_parts.append("\n[Following Sentences:]")
            context_parts.extend(merged_sentences[i + 1:end_index])

        # create context
        context = '\n'.join(context_parts) if context_parts else "No context available."
        # create ContextualSentence object
        contextual_sentences.append(ContextualSentence(
            sentence=sentence.strip(),
            context=context,
            index=i,
        ))
    return contextual_sentences
    
        

if __name__ == "__main__":
    # run a simple test to ensure it works
    text = """
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
    sentences = sentence_splitter(text, p_sentences=2, f_sentences=2)
    for i, cs in enumerate(sentences):
        print(f"\n🔸 Sentence {i + 1}:")
        print(f"Original: {cs.sentence}")
        print(f"Index: {cs.index}")
        print(f"Context preview: {cs.context}")
        print("-" * 40)

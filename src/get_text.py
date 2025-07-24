import re
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled, YouTubeTranscriptApi


def extract_from_url_withtimestamps(url: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Extracts timestamped transcript segments from a YouTube video.

    Args:
        url (str): The YouTube video URL.

    Returns:
        Tuple[List[Dict[str, Any]], str]: A list of transcript segments (each with 'start' and 'text'),
                                          and the language code of the transcript ('en' or 'ar').

    Raises:
        ValueError: If the URL is invalid.
        TranscriptsDisabled: If transcripts are disabled for the video.
        NoTranscriptFound: If no transcript is available.
        Exception: For other unexpected errors.
    """

    parsed = urlparse(url)
    if parsed.hostname and 'youtube.com' in parsed.hostname:
        video_id = parse_qs(parsed.query).get('v', [None])[0]
    elif parsed.hostname and 'youtu.be' in parsed.hostname:
        video_id = parsed.path.lstrip('/')
    else:
        raise ValueError("Invalid YouTube URL")

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    language = None
    transcript_output = []

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prefer manual, fallback to auto
        for lang in ['en', 'ar']:
            try:
                transcript = transcripts.find_manually_created_transcript([lang])
                language = lang
                break
            except NoTranscriptFound:
                continue

        if not language:
            for lang in ['en', 'ar']:
                try:
                    transcript = transcripts.find_generated_transcript([lang])
                    language = lang
                    break
                except NoTranscriptFound:
                    continue

        if not language:
            raise NoTranscriptFound("No transcript available in 'en' or 'ar'")

        transcript_data = transcript.fetch()

        for entry in transcript_data:
            text = entry.text.strip()
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\[.*?\]', '', text).strip()

            if not text:
                continue

            transcript_output.append({
                "start": round(entry.start, 2),
                "text": text
            })

        return transcript_output, language

    except TranscriptsDisabled:
        raise TranscriptsDisabled("Transcripts are disabled for this video")
    except NoTranscriptFound as e:
        raise NoTranscriptFound(f"No transcript available: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")
    
if __name__ == "__main__":
    # Example usage
    url = "https://www.youtube.com/watch?v=pzBi1nwDn8U"
    try:
        transcript, lang = extract_from_url_withtimestamps(url)
        print(f"Transcript Language: {lang}")
        print(transcript)
    except Exception as e:
        print(f"Error: {str(e)}")
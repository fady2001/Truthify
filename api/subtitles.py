from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        try:
            # Parse query parameters from the URL
            parsed_url = urlparse(self.path)
            query_params = {
                k: v[0] if v else "" for k, v in parse_qs(parsed_url.query).items()
            }

            video_id = query_params.get("videoId")
            lang = query_params.get("lang", "en")  # Default to Arabic

            if not video_id:
                self.send_error_response(400, {"error": "Missing videoId parameter"})
                return

            # Try to fetch transcript with preferred language(s)
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=[lang, "ar", "en"]
            )

            response_data = {
                "videoId": video_id,
                "language": lang,
                "count": len(transcript),
                "subtitles": transcript,
            }

            self.send_success_response(response_data)

        except TranscriptsDisabled:
            self.send_error_response(
                403, {"error": "Subtitles are disabled for this video"}
            )

        except NoTranscriptFound:
            self.send_error_response(
                404, {"error": f"No subtitles found for language {lang}"}
            )

        except VideoUnavailable:
            self.send_error_response(404, {"error": "Video is unavailable"})

        except Exception as e:
            self.send_error_response(500, {"error": str(e)})

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error_response(self, status_code, error_data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(error_data).encode())

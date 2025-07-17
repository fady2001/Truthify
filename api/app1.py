import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/subtitles", methods=["GET"])
def get_subtitles():
    try:
        video_id = request.args.get("videoId")
        lang = request.args.get("lang", "en")

        if not video_id:
            return jsonify({"error": "Missing videoId parameter"}), 400

        # Try to fetch transcript with preferred language(s)
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=[lang, "ar", "en"]
        )

        return jsonify(
            {
                "videoId": video_id,
                "language": lang,
                "count": len(transcript),
                "subtitles": transcript,
            }
        ), 200

    except TranscriptsDisabled:
        return jsonify({"error": "Subtitles are disabled for this video"}), 403

    except NoTranscriptFound:
        return jsonify({"error": f"No subtitles found for language {lang}"}), 404

    except VideoUnavailable:
        return jsonify({"error": "Video is unavailable"}), 404

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/", methods=["GET"])
def homepage():
    return jsonify({"status": "success", "message": "Truthify API is running"}), 200


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"}), 200


# Error handlers for better debugging
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

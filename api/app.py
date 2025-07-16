from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = Flask(__name__)

@app.route('/subtitles', methods=['GET'])
def get_subtitles():
    video_id = request.args.get('videoId')
    lang = request.args.get('lang', 'en')
    if not video_id:
        return jsonify({'error': 'Missing videoId parameter'}), 400

    try:
        # Try to fetch transcript with preferred language(s)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang, 'ar', 'en'])

        return jsonify({
            'videoId': video_id,
            'language': lang,
            'count': len(transcript),
            'subtitles': transcript
        })

    except TranscriptsDisabled:
        return jsonify({'error': 'Subtitles are disabled for this video'}), 403

    except NoTranscriptFound:
        return jsonify({'error': f'No subtitles found for language {lang}'}), 404

    except VideoUnavailable:
        return jsonify({'error': 'Video is unavailable'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify, session
import os
import uuid
import traceback
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'interview-ai-secret-2024'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

QUESTIONS = [
    "Tell me about yourself and your professional background.",
    "What are your greatest strengths and weaknesses?",
    "Why do you want to work for our company?",
    "Describe a challenging situation and how you handled it.",
    "Where do you see yourself in 5 years?",
    "Why should we hire you over other candidates?",
    "Tell me about a time you worked in a team under pressure.",
    "How do you handle conflict in the workplace?",
    "What motivates you to perform your best?",
    "Describe your leadership style with an example."
    "What is your biggest professional achievement?",
]


@app.route('/')
def index():
    import random
    question = random.choice(QUESTIONS)
    session['current_question'] = question
    return render_template('index.html', question=question)


@app.route('/submit', methods=['POST'])
def submit():
    # Wrap EVERYTHING in try/except so Flask always returns JSON, never HTML error page
    try:
        question = session.get('current_question', QUESTIONS[0])

        video_file = request.files.get('video')
        unique_id = str(uuid.uuid4())[:8]
        video_path = None

        # Save video
        if video_file and video_file.filename:
            video_path = os.path.join(UPLOAD_FOLDER, f'video_{unique_id}.webm')
            video_file.save(video_path)

        # ── Step 1: Face Analysis ──
        face_results = {
            'confidence_score': 50,
            'dominant_emotion': 'neutral',
            'emotion_breakdown': {},
            'tips': ['Camera clearly nahi dikhi. Dobara try karein.']
        }

        if video_path and os.path.exists(video_path):
            try:
                from ai.face_analyzer import analyze_video_emotions
                face_results = analyze_video_emotions(video_path)
            except Exception as e:
                print(f"[Face Analysis Error] {e}")
                face_results['tips'] = [f'Face analysis skip hua: {str(e)[:80]}']

        # ── Step 2: Transcription ──
        transcript = ""
        if video_path and os.path.exists(video_path):
            try:
                from ai.answer_evaluator import transcribe_from_video
                transcript = transcribe_from_video(video_path)
            except Exception as e:
                print(f"[Transcription Error] {e}")
                transcript = ""

        if not transcript:
            transcript = "Audio transcription unavailable. Please speak clearly into the microphone."

        # ── Step 3: AI Evaluation ──
        ai_results = {
            'score': 55,
            'overall_feedback': 'Answer evaluate nahi ho saka. API key check karein.',
            'strengths': ['You attempted the question'],
            'improvements': ['Speak more clearly', 'Use the STAR method', 'Give specific examples'],
            'model_answer_hint': 'Structure your answer with a clear opening, supporting points, and conclusion.'
        }

        skip_phrases = ["unavailable", "samajh nahi", "Error:"]
        should_evaluate = transcript and not any(p in transcript for p in skip_phrases)

        if should_evaluate:
            try:
                from ai.answer_evaluator import evaluate_answer
                ai_results = evaluate_answer(question, transcript)
            except Exception as e:
                print(f"[AI Evaluation Error] {e}")
                ai_results['overall_feedback'] = f'Evaluation error: {str(e)[:100]}'

        # ── Step 4: Final Score ──
        final_score = round(
            (face_results['confidence_score'] * 0.35) +
            (ai_results['score'] * 0.65)
        )
        final_score = max(0, min(100, final_score))

        # Cleanup
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception:
                pass

        return jsonify({
            'success': True,
            'question': question,
            'transcript': transcript,
            'final_score': final_score,
            'face': face_results,
            'ai': ai_results
        })

    except Exception as e:
        # CRITICAL: Always return JSON even on crash
        print(f"[SUBMIT CRASH] {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'question': session.get('current_question', ''),
            'transcript': 'Error occurred during processing.',
            'final_score': 0,
            'face': {
                'confidence_score': 0,
                'dominant_emotion': 'unknown',
                'tips': ['An error occurred. Please check your setup and try again.']
            },
            'ai': {
                'score': 0,
                'overall_feedback': f'Server error: {str(e)}',
                'strengths': [],
                'improvements': ['Check that all dependencies are installed: pip install -r requirements.txt'],
                'model_answer_hint': 'Please try again after fixing the error.'
            }
        }), 200  # Return 200 so browser doesn't reject it


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/new-question')
def new_question():
    try:
        import random
        question = random.choice(QUESTIONS)
        session['current_question'] = question
        return jsonify({'question': question})
    except Exception as e:
        return jsonify({'question': QUESTIONS[0], 'error': str(e)})


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route not found', 'message': str(e)}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error', 'message': str(e)}), 200


if __name__ == '__main__':
    print("\n✅ InterviewAI Server Starting...")
    print("📍 Open: http://localhost:5000\n")
    app.run(debug=True, port=5000)
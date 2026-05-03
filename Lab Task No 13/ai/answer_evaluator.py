import os
import json


def transcribe_from_video(video_path: str) -> str:
    """
    Video file se audio extract karke text mein convert karta hai.
    ffmpeg + SpeechRecognition use karta hai.
    """
    if not os.path.exists(video_path):
        return ""

    # Extract audio from webm using ffmpeg
    audio_path = video_path.replace('.webm', '_audio.wav')

    try:
        ret = os.system(
            f'ffmpeg -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}" -y -loglevel quiet'
        )
        if ret != 0 or not os.path.exists(audio_path):
            raise RuntimeError("ffmpeg audio extraction failed")

        text = _transcribe_wav(audio_path)
        return text

    except FileNotFoundError:
        # ffmpeg not installed
        return _try_direct_transcription(video_path)
    except Exception as e:
        print(f"[Transcribe] Error: {e}")
        return ""
    finally:
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass


def _transcribe_wav(audio_path: str) -> str:
    """WAV file ko text mein convert karo using SpeechRecognition."""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='en-US')
        return text
    except ImportError:
        print("[Transcribe] SpeechRecognition not installed: pip install SpeechRecognition")
        return ""
    except Exception as e:
        print(f"[Transcribe WAV] {e}")
        return ""


def _try_direct_transcription(video_path: str) -> str:
    """ffmpeg na ho to direct try karo."""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(video_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language='en-US')
    except Exception:
        return ""


def evaluate_answer(question: str, answer: str) -> dict:
    """
    Claude AI se interview answer evaluate karwata hai.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key or api_key == "your_anthropic_api_key_here":
        return _demo_evaluation(question, answer)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are an expert interview coach. Evaluate this interview answer strictly and fairly.

Interview Question: {question}

Candidate's Answer: {answer}

Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{{
  "score": <integer 0-100>,
  "overall_feedback": "<2-3 concise sentences of overall assessment>",
  "strengths": ["<specific strength 1>", "<specific strength 2>"],
  "improvements": ["<specific improvement 1>", "<specific improvement 2>", "<specific improvement 3>"],
  "model_answer_hint": "<One sentence hint about what an ideal answer includes>"
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()
        # Remove markdown fences if present
        raw = raw.replace('```json', '').replace('```', '').strip()

        result = json.loads(raw)

        # Validate required fields
        required = ['score', 'overall_feedback', 'strengths', 'improvements', 'model_answer_hint']
        for key in required:
            if key not in result:
                raise ValueError(f"Missing key: {key}")

        result['score'] = max(0, min(100, int(result['score'])))
        return result

    except ImportError:
        print("[Evaluate] anthropic not installed: pip install anthropic")
        return _demo_evaluation(question, answer)
    except json.JSONDecodeError as e:
        print(f"[Evaluate] JSON parse error: {e}")
        return _demo_evaluation(question, answer)
    except Exception as e:
        print(f"[Evaluate] Error: {e}")
        return _demo_evaluation(question, answer)


def _demo_evaluation(question: str, answer: str) -> dict:
    """
    API key na ho ya error ho to demo evaluation return karo.
    Answer ki basic qualities check karta hai.
    """
    word_count = len(answer.split()) if answer else 0

    # Basic heuristic scoring
    score = 50
    strengths = []
    improvements = []

    if word_count > 50:
        score += 10
        strengths.append('You gave a detailed response with good length.')
    elif word_count > 20:
        score += 5
        strengths.append('You attempted to answer the question.')
    else:
        improvements.append('Your answer was too short. Aim for 60-120 words minimum.')

    star_keywords = ['situation', 'task', 'action', 'result', 'when', 'team', 'project', 'achieved']
    matched = [k for k in star_keywords if k in answer.lower()]
    if len(matched) >= 3:
        score += 15
        strengths.append('You used situational storytelling effectively.')
    else:
        improvements.append('Use the STAR method: Situation → Task → Action → Result.')

    if any(w in answer.lower() for w in ['i', 'my', 'me', 'we']):
        score += 5
        strengths.append('You spoke from personal experience.')

    if not strengths:
        strengths = ['You made an attempt at the question.']

    improvements += [
        'Add specific numbers or metrics to strengthen your answer.',
        'Practice out loud to improve delivery and pacing.',
    ]

    return {
        'score': min(score, 85),
        'overall_feedback': (
            'This is a demo evaluation (add ANTHROPIC_API_KEY in .env for full AI feedback). '
            f'Your answer contained {word_count} words. '
            'Structure and content analysis shown below.'
        ),
        'strengths': strengths[:3],
        'improvements': improvements[:3],
        'model_answer_hint': (
            'A strong answer uses the STAR method, includes specific examples, '
            'and connects your experience to the role requirements.'
        )
    }
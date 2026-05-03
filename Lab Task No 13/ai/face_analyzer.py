import os


def analyze_video_emotions(video_path: str) -> dict:
    """
    Video frames se emotion detect karta hai.
    DeepFace available na ho to graceful fallback deta hai.
    """
    default = {
        'confidence_score': 60,
        'dominant_emotion': 'neutral',
        'emotion_breakdown': {},
        'tips': []
    }

    if not os.path.exists(video_path):
        default['tips'] = ['Video file nahi mili.']
        return default

    # Try OpenCV + DeepFace
    try:
        import cv2
        from deepface import DeepFace
        return _analyze_with_deepface(video_path, cv2, DeepFace)
    except ImportError:
        print("[Face] DeepFace/OpenCV not installed. Using fallback score.")
        default['tips'] = [
            'Install deepface for real face analysis: pip install deepface opencv-python',
            'Face analysis skipped — answer score still calculated.'
        ]
        return default
    except Exception as e:
        print(f"[Face] Analysis failed: {e}")
        default['tips'] = [f'Face analysis error: {str(e)[:80]}']
        return default


def _analyze_with_deepface(video_path, cv2, DeepFace) -> dict:
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {
            'confidence_score': 50,
            'dominant_emotion': 'neutral',
            'emotion_breakdown': {},
            'tips': ['Video file open nahi ho saki.']
        }

    emotions_list = []
    frame_count = 0
    sample_every = 30  # Har 30 frames mein 1 analyze

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % sample_every != 0:
            continue
        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            dominant = result[0]['dominant_emotion']
            emotions_list.append(dominant)
        except Exception:
            pass

    cap.release()

    if not emotions_list:
        return {
            'confidence_score': 50,
            'dominant_emotion': 'neutral',
            'emotion_breakdown': {},
            'tips': ['Chehra detect nahi hua. Camera ke saamne clearly baith kar dobara try karein.']
        }

    from collections import Counter
    counts = Counter(emotions_list)
    dominant_overall = counts.most_common(1)[0][0]
    total = len(emotions_list)

    positive = {'happy', 'neutral', 'surprise'}
    positive_count = sum(1 for e in emotions_list if e in positive)
    confidence_score = round((positive_count / total) * 100)

    tips = _generate_tips(dominant_overall, confidence_score)

    return {
        'confidence_score': confidence_score,
        'dominant_emotion': dominant_overall,
        'emotion_breakdown': dict(counts),
        'tips': tips
    }


def _generate_tips(emotion: str, score: int) -> list:
    tips = []
    emotion_tips = {
        'angry':   'Expression soft rakho — interviewer ke sath friendly rehna zaroori hai.',
        'fear':    'Ghabrao mat — deep breaths lo aur confident posture rakho.',
        'sad':     'Thodi enthusiasm add karo — smile se energy dikhao.',
        'disgust': 'Neutral ya positive expression maintain karo throughout.',
        'happy':   'Zabardast! Aapka expression confident aur welcoming tha.',
        'neutral': 'Thodi aur warmth add karo — occasional smile confidence show karta hai.',
        'surprise':'Controlled expressions rakho — calm aur composed lagein.',
    }
    if emotion in emotion_tips:
        tips.append(emotion_tips[emotion])

    if score < 40:
        tips.append('Camera se eye contact improve karo — seedha lens mein dekho.')
        tips.append('Daily 5 min mirror practice karo facial expressions ke liye.')
    elif score < 70:
        tips.append('Acchi progress! Posture aur smile par thoda aur dhyan dein.')
    else:
        tips.append('Excellent facial confidence! Aise hi jaari rakhein.')

    return tips
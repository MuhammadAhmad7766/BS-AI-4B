# InterviewAI

InterviewAI is a Flask-based web application designed to help job seekers practice their interview skills through AI-driven video analysis. The system provides feedback by evaluating both the content of the user's spoken answers and their facial expressions during the recording.

## 🚀 Features

*   **Random Question Generation**: Dynamically selects from a curated list of common behavioral interview questions.
*   **Video Response Analysis**: Captures and processes video submissions to analyze facial expressions and confidence levels.
*   **Speech-to-Text Transcription**: Automatically transcribes video responses into text for content evaluation.
*   **AI Evaluation**: Scores answers based on professional standards, offering specific feedback on strengths and improvements.
*   **Hybrid Scoring**: Calculates a final score using a weighted average of facial confidence (35%) and answer quality (65%)[cite: 1].
*   **Robust Error Handling**: Designed to return JSON feedback even in the event of processing failures to ensure a smooth user experience[cite: 1].

## 🛠️ Project Structure

The application is modularized into several key components:
*   **`app.py`**: The main Flask entry point handling routing, session management, and the submission pipeline[cite: 1].
*   **`ai/face_analyzer.py`**: Handles emotion detection and facial confidence scoring[cite: 1].
*   **`ai/answer_evaluator.py`**: Manages audio transcription and AI-based answer scoring[cite: 1].
*   **`uploads/`**: Temporary storage for video processing; files are removed after evaluation[cite: 1].

## 📋 Prerequisites

*   Python 3.x[cite: 1]
*   Flask and Flask-Session[cite: 1]
*   `python-dotenv` for environment variable management[cite: 1]
*   AI modules for face analysis and transcription (as referenced in `app.py`)[cite: 1]

## ⚙️ Installation & Setup

1.  **Clone the repository** to your local machine.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt

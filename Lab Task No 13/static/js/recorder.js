let mediaRecorder = null;
let videoChunks = [];
let stream = null;
let timerInterval = null;
let seconds = 0;
let isRecording = false;

// On page load — start camera
window.addEventListener('load', () => {
  initCamera();
});

async function initCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    const video = document.getElementById('videoPreview');
    video.srcObject = stream;
    video.onloadedmetadata = () => video.play();
    document.getElementById('videoOverlay').style.display = 'none';
    setStatus('Camera ready — read the question and press record.');
  } catch (err) {
    console.error('Camera error:', err);
    setStatus('Camera access denied — allow camera & microphone and reload.');
  }
}

async function startRecording() {
  if (isRecording) return;

  if (!stream) {
    await initCamera();
    if (!stream) return;
  }

  videoChunks = [];

  // Pick best supported format
  const mimeTypes = [
    'video/webm;codecs=vp9,opus',
    'video/webm;codecs=vp8,opus',
    'video/webm',
    'video/mp4',
  ];
  const mimeType = mimeTypes.find(m => MediaRecorder.isTypeSupported(m)) || '';

  try {
    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
  } catch (e) {
    mediaRecorder = new MediaRecorder(stream);
  }

  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) videoChunks.push(e.data);
  };

  mediaRecorder.onerror = (e) => {
    console.error('MediaRecorder error:', e);
    setStatus('Recording error — please try again.');
  };

  mediaRecorder.start(200);
  isRecording = true;

  document.getElementById('startBtn').classList.add('hidden');
  document.getElementById('stopBtn').classList.remove('hidden');
  document.getElementById('recIndicator').classList.add('active');
  setStatus('Recording your answer…');
  startTimer();
}

async function stopRecording() {
  if (!mediaRecorder || !isRecording) return;

  isRecording = false;
  stopTimer();

  document.getElementById('stopBtn').classList.add('hidden');
  document.getElementById('startBtn').classList.remove('hidden');
  document.getElementById('recIndicator').classList.remove('active');
  setStatus('Processing your answer…');

  // Wait for final chunks
  await new Promise((resolve) => {
    mediaRecorder.onstop = resolve;
    mediaRecorder.stop();
  });

  showLoading();
  animateLoadingSteps();
  await submitRecording();
}

async function submitRecording() {
  if (videoChunks.length === 0) {
    hideLoading();
    setStatus('No recording data. Please try again.');
    return;
  }

  const blob = new Blob(videoChunks, { type: videoChunks[0]?.type || 'video/webm' });

  if (blob.size < 1000) {
    hideLoading();
    setStatus('Recording too short. Hold "Stop & Analyze" after speaking.');
    return;
  }

  const formData = new FormData();
  formData.append('video', blob, 'recording.webm');

  try {
    const response = await fetch('/submit', {
      method: 'POST',
      body: formData,
    });

    // Check if response is actually JSON
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      const text = await response.text();
      console.error('Server returned non-JSON:', text.slice(0, 300));
      throw new Error('Server error — check your terminal for details.');
    }

    const results = await response.json();

    if (results.error && !results.success) {
      console.warn('Server returned error result:', results.error);
    }

    // Save to localStorage and go to dashboard
    localStorage.setItem('interviewResults', JSON.stringify(results));

    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 800);

  } catch (err) {
    console.error('Submit error:', err);
    hideLoading();
    setStatus('Error: ' + err.message);
  }
}

async function getNewQuestion() {
  try {
    const res = await fetch('/new-question');
    const contentType = res.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) throw new Error('Server error');
    const data = await res.json();
    document.getElementById('questionText').textContent = data.question;
    setStatus('New question loaded. Press record when ready.');
  } catch (err) {
    console.error('New question error:', err);
  }
}

function animateLoadingSteps() {
  const steps = ['step1', 'step2', 'step3', 'step4'];
  steps.forEach((id, i) => {
    setTimeout(() => {
      if (i > 0) {
        const prev = document.getElementById(steps[i - 1]);
        if (prev) {
          prev.classList.remove('active');
          prev.classList.add('done');
        }
      }
      const el = document.getElementById(id);
      if (el) el.classList.add('active');
    }, i * 2800);
  });
}

function showLoading() {
  const el = document.getElementById('loadingOverlay');
  if (el) el.classList.remove('hidden');
}

function hideLoading() {
  const el = document.getElementById('loadingOverlay');
  if (el) el.classList.add('hidden');
}

function setStatus(msg) {
  const el = document.getElementById('statusBar');
  if (el) el.textContent = msg;
}

function startTimer() {
  seconds = 0;
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    seconds++;
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    const el = document.getElementById('timer');
    if (el) el.textContent = `${m}:${s}`;
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}
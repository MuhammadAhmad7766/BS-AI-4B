import cv2
import os
from flask import Flask, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load the pre-trained Haar Cascade (Standard with OpenCV)
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)

            # OpenCV Processing
            img = cv2.imread(path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            objects = detector.detectMultiScale(gray, 1.1, 4)

            # Draw rectangles and count
            count = 0
            for (x, y, w, h) in objects:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                count += 1

            # Save the result image
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_' + file.filename)
            cv2.imwrite(result_path, img)

            return render_template('index.html', count=count, image='result_' + file.filename)
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
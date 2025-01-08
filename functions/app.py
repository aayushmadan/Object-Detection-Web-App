from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import torch

app = Flask(__name__, template_folder='public')

# Set up YOLO model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO("yolov8n.pt")
model.to(device)

# Initialize video capture
camera = cv2.VideoCapture(0)  # Use 0 for the default camera, change if needed


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Resize the frame for consistent processing
        frame_resized = cv2.resize(frame, (640, 480))

        # YOLO inference
        results = model(frame_resized, conf=0.5, device=device)

        # Get detection results
        detections = results[0].boxes.xyxy.cpu().numpy() if len(results[0]) > 0 else []

        if len(detections) > 0:
            # Annotate only if detections are present
            annotated_frame = results[0].plot()
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        else:
            # No detections: Display original frame without modifications
            annotated_frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        # Encode the frame for streaming
        _, buffer = cv2.imencode('.jpg', annotated_frame_rgb)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

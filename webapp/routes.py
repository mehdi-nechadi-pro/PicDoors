from flask import Blueprint, render_template, Response
# On importe le générateur depuis le module core
from core.recognition import generate_frames 

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
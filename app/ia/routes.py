from flask import Blueprint, Response
from .camera import VideoManager 

ia_bp = Blueprint('ia', __name__)

video_manager = VideoManager()

@ia_bp.route('/video_feed')
def video_feed():
    return Response(video_manager.generate_stream(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')
import os

# Configuration Réseau
CAMERA_IP = "192.168.1.155"
CAMERA_PORT = "4747"
STREAM_URL = f"http://{CAMERA_IP}:{CAMERA_PORT}/video"

# Configuration IA
MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "mtcnn"
THRESHOLD = 0.30
CHECK_INTERVAL = 10  # Secondes entre chaque analyse
DISPLAY_TIME = 2   

# Chemins des fichiers (Absolus pour éviter les erreurs)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ia/data", "master_embeddings_db.json")

# Configuration Back
API_URL = "http://127.0.0.1:8000" 
SENSOR_ENDPOINT = f"{API_URL}/api/sensors"
DETECTED_ENDPOINT = f"{API_URL}/api/detected"
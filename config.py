import os

# Configuration Réseau
CAMERA_IP = "10.14.55.189"
CAMERA_PORT = "4747"
STREAM_URL = f"http://{CAMERA_IP}:{CAMERA_PORT}/video"

# Configuration IA
MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "mtcnn"
THRESHOLD = 0.30
CHECK_INTERVAL = 10  # Secondes entre chaque analyse
DISPLAY_TIME = 2    # Temps d'affichage du résultat

# Chemins des fichiers (Absolus pour éviter les erreurs)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "master_embeddings_db.json")

# Configuration Arduino
ARDUINO_PORT = "/dev/cu.usbmodem1301" # Remplacez par COM3 sous Windows si besoin
ARDUINO_BAUDRATE = 9600
PIN_LED_VERT = 13  # Exemple de pin
PIN_LED_ROUGE = 12
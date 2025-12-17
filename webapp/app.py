import cv2
import numpy as np
import json
import time
from deepface import DeepFace
import config  # <--- On importe tout depuis votre fichier config.py
from hardware.arduino_manager import ArduinoController

# Initialisation du contrôleur Arduino (si branché)
try:
    arduino = ArduinoController()
except Exception:
    arduino = None

# Variables Globales d'état (Celles-ci doivent rester ici car elles changent pendant l'exécution)
database = {}
last_analysis_time = 0
current_result = None
result_display_end = 0

def load_database():
    """Charge la base de données définie dans config.py"""
    try:
        # On utilise config.DB_PATH au lieu d'une variable locale
        with open(config.DB_PATH, 'r') as f:
            db = json.load(f)
        print(f"✅ Base chargée : {len(db)} personnes.")
        return db
    except FileNotFoundError:
        print(f"❌ ERREUR CRITIQUE : Le fichier {config.DB_PATH} est introuvable.")
        return {}

def find_best_match(target_embedding, db):
    """Logique de comparaison mathématique (Cosinus)"""
    max_similarity = -1.0
    best_match_name = "Inconnu"
    target_vector = np.array(target_embedding)
    norm_target = np.linalg.norm(target_vector)

    for name, db_embedding_list in db.items():
        db_vector = np.array(db_embedding_list)
        if np.linalg.norm(db_vector) == 0: continue
            
        dot_product = np.dot(target_vector, db_vector)
        norm_db = np.linalg.norm(db_vector)
        
        # Sécurité division par zéro
        if norm_target * norm_db == 0: continue

        similarity = dot_product / (norm_target * norm_db)
        
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_name = name

    return best_match_name, max_similarity

# Chargement initial de la base
database = load_database()

def generate_frames():
    """Générateur de flux vidéo optimisé"""
    global last_analysis_time, current_result, result_display_end
    
    # Utilisation de l'URL depuis la config
    cap = cv2.VideoCapture(config.STREAM_URL)
    
    # Optimisation Latence : Buffer à 1
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        success, frame = cap.read()
        if not success:
            cap.release()
            time.sleep(0.5)
            cap = cv2.VideoCapture(config.STREAM_URL)
            continue

        # Rotation (Toujours en dur ou à mettre dans config si ça change souvent)
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Optimisation Performance : Resize en 640px de large
        height, width = frame.shape[:2]
        new_width = 640
        new_height = int(height * (new_width / width))
        frame = cv2.resize(frame, (new_width, new_height))

        now = time.time()

        # --- ANALYSE IA (Selon l'intervalle du config.py) ---
        if now - last_analysis_time >= config.CHECK_INTERVAL:
            last_analysis_time = now
            try:
                # Utilisation des paramètres du config.py
                results = DeepFace.represent(
                    img_path=frame,
                    model_name=config.MODEL_NAME,
                    detector_backend=config.DETECTOR_BACKEND,
                    enforce_detection=True
                )
                
                target_embedding = results[0]['embedding']
                facial_area = results[0]['facial_area']
                name, score = find_best_match(target_embedding, database)

                # Vérification du seuil depuis config.py
                if score >= config.THRESHOLD:
                    msg = f"{name} ({score:.2f})"
                    color = (0, 255, 0) # Vert
                    
                    # Ordre Arduino (si connecté)
                    if arduino: arduino.grant_access(name)
                else:
                    msg = f"Inconnu ({score:.2f})"
                    color = (0, 0, 255) # Rouge
                    
                    # Ordre Arduino (si connecté)
                    if arduino: arduino.deny_access()

                current_result = {"box": facial_area, "msg": msg, "color": color}
                
                # Durée d'affichage depuis config.py
                result_display_end = now + config.DISPLAY_TIME

            except ValueError:
                pass # Pas de visage détecté
            except Exception as e:
                print(f"Erreur IA: {e}")

        # --- DESSIN ---
        if current_result and now < result_display_end:
            # Récupération des coordonnées adaptées à l'image redimensionnée
            x, y, w, h = current_result['box']['x'], current_result['box']['y'], current_result['box']['w'], current_result['box']['h']
            color = current_result['color']
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(frame, (x, y-30), (x+w, y), color, -1)
            cv2.putText(frame, current_result['msg'], (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # --- COMPTE À REBOURS ---
        elapsed = now - last_analysis_time
        countdown = max(0, config.CHECK_INTERVAL - elapsed)
        
        # Affichage discret du temps restant
        if countdown < 0.5:
            cv2.putText(frame, "Analyse...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            cv2.putText(frame, f"Scan: {countdown:.0f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        # Encodage JPEG compressé (60%) pour fluidité réseau
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        if ret:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
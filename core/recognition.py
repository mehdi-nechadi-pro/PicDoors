import cv2
import numpy as np
import json
import time
from deepface import DeepFace
import config  # On importe notre config

# Variables d'état globales pour ce module
database = {}
last_analysis_time = 0
current_result = None
result_display_end = 0

def load_database():
    """Charge la base de données au démarrage"""
    try:
        with open(config.DB_PATH, 'r') as f:
            db = json.load(f)
        print(f"✅ Base chargée : {len(db)} personnes.")
        return db
    except FileNotFoundError:
        print(f"❌ ERREUR CRITIQUE : {config.DB_PATH} introuvable.")
        return {}

def find_best_match(target_embedding, db):
    """Logique de comparaison mathématique"""
    max_similarity = -1.0
    best_match_name = "Inconnu"
    target_vector = np.array(target_embedding)
    norm_target = np.linalg.norm(target_vector)

    for name, db_embedding_list in db.items():
        db_vector = np.array(db_embedding_list)
        if np.linalg.norm(db_vector) == 0: continue
            
        # Cosine Similarity
        dot_product = np.dot(target_vector, db_vector)
        norm_db = np.linalg.norm(db_vector)
        similarity = dot_product / (norm_target * norm_db)
        
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_name = name

    return best_match_name, max_similarity

# Chargement initial unique
database = load_database()

def generate_frames():
    """Générateur de flux vidéo pour Flask"""
    global last_analysis_time, current_result, result_display_end
    
    cap = cv2.VideoCapture(config.STREAM_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        success, frame = cap.read()
        if not success:
            cap.release()
            time.sleep(0.5)
            cap = cv2.VideoCapture(config.STREAM_URL)
            continue

        # Rotation (Adaptée pour le portrait)
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        now = time.time()

        # --- ANALYSE IA (Périodique) ---
        if now - last_analysis_time >= config.CHECK_INTERVAL:
            last_analysis_time = now
            try:
                results = DeepFace.represent(
                    img_path=frame,
                    model_name=config.MODEL_NAME,
                    detector_backend=config.DETECTOR_BACKEND,
                    enforce_detection=True
                )
                
                # Récupération données
                target_embedding = results[0]['embedding']
                facial_area = results[0]['facial_area']
                name, score = find_best_match(target_embedding, database)

                if score >= config.THRESHOLD:
                    msg = f"{name} ({score:.2f})"
                    color = (0, 255, 0) # Vert
                    # TODO: Ajouter ici l'envoi vers Arduino
                else:
                    msg = f"Inconnu ({score:.2f})"
                    color = (0, 0, 255) # Rouge

                current_result = {"box": facial_area, "msg": msg, "color": color}
                result_display_end = now + config.DISPLAY_TIME
                print(f"🔍 Résultat : {msg}")

            except ValueError:
                pass # Aucun visage
            except Exception as e:
                print(f"Erreur IA: {e}")

        # --- DESSIN ---
        if current_result and now < result_display_end:
            x, y, w, h = current_result['box']['x'], current_result['box']['y'], current_result['box']['w'], current_result['box']['h']
            color = current_result['color']
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(frame, (x, y-30), (x+w, y), color, -1)
            cv2.putText(frame, current_result['msg'], (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Countdown visuel
        elapsed = now - last_analysis_time
        countdown = max(0, config.CHECK_INTERVAL - elapsed)
        if countdown < 0.5:
            cv2.putText(frame, "Analyse...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            cv2.putText(frame, f"Scan: {countdown:.1f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Encodage JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
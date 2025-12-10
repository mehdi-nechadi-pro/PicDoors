import cv2
import numpy as np
import json
from deepface import DeepFace

# --- CONFIGURATION ---
DB_FILE = "master_embeddings_db.json"  # Votre fichier généré précédemment
MODEL_NAME = "ArcFace"                 # Doit être le MÊME que pour l'inscription
DETECTOR_BACKEND = "mtcnn"             # Doit être cohérent
THRESHOLD = 0.30                       # Seuil de décision (0.5 est standard pour ArcFace)
ip = "10.14.55.189"
port = "4747"

STREAM_URL = f"http://{ip}:{port}/video"

# ---------------------

def load_database(db_path):
    """Charge les embeddings de référence depuis le JSON."""
    try:
        with open(db_path, 'r') as f:
            db = json.load(f)
        print(f"✅ Base de données chargée : {len(db)} personnes trouvées.")
        return db
    except FileNotFoundError:
        print(f"❌ ERREUR : Le fichier {db_path} est introuvable.")
        exit()

def find_best_match(target_embedding, database):
    """
    Compare l'embedding cible avec toute la base de données.
    Retourne (Nom, Score) du meilleur candidat.
    """
    max_similarity = -1.0
    best_match_name = "Inconnu"

    # Convertir la cible en vecteur NumPy une fois pour toutes
    target_vector = np.array(target_embedding)
    norm_target = np.linalg.norm(target_vector)

    for name, db_embedding_list in database.items():
        # Convertir la référence en vecteur NumPy
        db_vector = np.array(db_embedding_list)
        
        # --- CALCUL MATHÉMATIQUE (Similarité Cosinus) ---
        # Formule : (A . B) / (||A|| * ||B||)
        dot_product = np.dot(target_vector, db_vector)
        norm_db = np.linalg.norm(db_vector)
        
        similarity = dot_product / (norm_target * norm_db)
        # ------------------------------------------------
        
        # On cherche la similarité la plus élevée (proche de 1.0)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_name = name

    return best_match_name, max_similarity

# --- MAIN ---

# 1. Chargement de la Base de Données
database = load_database(DB_FILE)

# 2. Démarrage de la Webcam
cap = cv2.VideoCapture(STREAM_URL) # 0 est généralement la webcam par défaut

print("\n--- SYSTÈME PRÊT ---")
print("📹 Appuyez sur 'S' pour prendre un screen et identifier.")
print("❌ Appuyez sur 'Q' pour quitter.")

import time
import cv2
import numpy as np
from deepface import DeepFace

# --- INITIALISATION DU TIMER ---
last_analysis_time = time.time()
CHECK_INTERVAL = 5  # secondes

# ... (Votre chargement de base de données et initialisation webcam ici) ...

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur de lecture webcam")
        break
    
    # 1. Rotation (comme dans votre code original)
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # 2. CROP : Supprimer le 1/3 du haut 
    height, width, _ = frame.shape
    start_y = int(height / 3) # On calcule le 1/3 de la hauteur
    frame = frame[start_y:, :] # On ne garde que du tiers jusqu'en bas
    
    # Affichage du flux vidéo en direct
    display_frame = frame.copy()
    
    # Calcul du temps restant pour l'affichage
    elapsed = time.time() - last_analysis_time
    countdown = max(0, CHECK_INTERVAL - elapsed)
    
    cv2.putText(display_frame, f"Scan dans: {countdown:.1f}s", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow('Reconnaissance Faciale', display_frame)

    key = cv2.waitKey(1) & 0xFF

    # --- DÉCLENCHEUR AUTOMATIQUE : TOUTES LES 5 SECONDES ---
    if time.time() - last_analysis_time >= CHECK_INTERVAL:
        last_analysis_time = time.time() # On reset le timer tout de suite
        
        print("\n📸 Capture Auto ! Analyse en cours...")
        
        try:
            results = DeepFace.represent(
                img_path=frame, 
                model_name=MODEL_NAME, 
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=True
            )
            
            # On prend le premier visage détecté
            target_embedding = results[0]['embedding']
            facial_area = results[0]['facial_area'] # x, y, w, h
            
            # Comparaison avec la base de données
            name_found, score = find_best_match(target_embedding, database)
            
            # Vérification du Seuil
            if score >= THRESHOLD:
                final_name = name_found
                color = (0, 255, 0) # Vert
                msg = f"IDENTIFIE: {final_name} ({score:.2f})"
            else:
                final_name = "Inconnu"
                color = (0, 0, 255) # Rouge
                msg = f"INCONNU (Max: {score:.2f})"

            print(f"👉 Résultat : {msg}")
            
            # PAUSE DE 2 SECONDES pour voir le résultat, puis ça repart
            cv2.waitKey(2000) 
            
            # On reset le timer après la pause pour avoir 5 vraies secondes de flux vidéo
            last_analysis_time = time.time() 

        except ValueError:
            print("⚠️ Aucun visage détecté dans la zone rognée !")
        except Exception as e:
            print(f"⚠️ Erreur: {e}")

    # --- QUITTER : TOUCHE 'Q' ---
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
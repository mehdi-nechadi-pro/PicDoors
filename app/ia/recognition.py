import json
import numpy as np
from deepface import DeepFace
import config 

class FaceEngine:
    def __init__(self):
        self.db = self._load_database()

    def _load_database(self):
        """Charge le fichier JSON des embeddings"""
        try:
            with open(config.DB_PATH, 'r') as f:
                data = json.load(f)
            print(f"[IA] Base chargee : {len(data)} profils")
            return data
        except Exception as e:
            print(f"[IA] Erreur chargement DB : {e}")
            return {}

    def process_image(self, img_array):
        """
        Analyse une image pour detecter et reconnaitre un visage.
        Retourne: (nom, score, zone) ou (None, 0, None)
        """
        try:
            results = DeepFace.represent(
                img_path=img_array,
                model_name=config.MODEL_NAME,
                detector_backend=config.DETECTOR_BACKEND,
                enforce_detection=True
            )
            
            embedding = results[0]['embedding']
            area = results[0]['facial_area']
            
            name, score = self._compare_embeddings(embedding)
            return name, score, area

        except ValueError:
            return None, 0, None
        except Exception as e:
            print(f"[IA] Erreur DeepFace : {e}")
            return None, 0, None

    def _compare_embeddings(self, target_embedding):
        """Calcule la similarite cosinus entre le vecteur cible et la base"""
        best_name = "Inconnu"
        max_score = -1.0
        
        target_vec = np.array(target_embedding)
        norm_target = np.linalg.norm(target_vec)

        for name, db_emb in self.db.items():
            db_vec = np.array(db_emb)
            norm_db = np.linalg.norm(db_vec)
            
            if norm_target * norm_db == 0: continue
            
            score = np.dot(target_vec, db_vec) / (norm_target * norm_db)
            if score > max_score:
                max_score = score
                best_name = name

        return best_name, max_score
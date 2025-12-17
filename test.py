import cv2
import numpy as np
import os
from insightface.app import FaceAnalysis

# 1. Initialisation du modèle (Mode CPU)
print("Chargement du modèle... (Patientez pour le téléchargement initial)")
app = FaceAnalysis(name='buffalo_s', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

def get_embedding(filename):
    if not os.path.exists(filename):
        print(f"Erreur : Le fichier '{filename}' n'existe pas.")
        return None
        
    img = cv2.imread(filename)
    if img is None:
        print(f"Erreur : Impossible de lire l'image '{filename}'.")
        return None

    # Détection
    faces = app.get(img)
    if not faces:
        print(f"Aucun visage trouvé dans {filename}")
        return None
        
    # On retourne la signature du premier visage
    return faces[0].embedding

# 2. Comparaison
# Modifiez les noms ici selon vos fichiers
file1 = "img/Nael1.jpg" 
file2 = "img/Mehdi1.jpg"

print(f"Comparaison de {file1} avec {file2}...")

emb1 = get_embedding(file1)
emb2 = get_embedding(file2)

if emb1 is not None and emb2 is not None:
    # Calcul de similarité (Produit scalaire normalisé)
    sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    print(f"\n---> Score de similarité : {sim:.4f}")
    
    if sim > 0.5:
        print("---> ✅ MÊME PERSONNE")
    else:
        print("---> ❌ PERSONNES DIFFÉRENTES")
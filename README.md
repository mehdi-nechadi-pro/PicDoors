#  PicDoors

PicDoors est un système de contrôle d'accès IoT intelligent.  
Il combine la **reconnaissance faciale biométrique** et une **authentification par code PIN** pour sécuriser l'ouverture d'une porte via un **servomoteur piloté par Arduino**.

---

##  Architecture du Projet

Le projet repose sur une **architecture distribuée en trois couches principales** qui communiquent en temps réel :

- **Dashboard Flask**  
  Interface web permettant de visualiser :
  - le flux vidéo en direct
  - l’état du système (*Veille*, *Scan*)

- **IA & Vision**  
  Module d’intelligence artificielle utilisant **DeepFace (ArcFace)** pour l’analyse biométrique.
  - Traite le flux vidéo reçu d’un smartphone (via **IP Webcam**)
  - Identifie les utilisateurs enregistrés
  

- **Backend & Hardware (FastAPI & Arduino)**  
  API de contrôle qui :
  - gère la logique métier (codes PIN, automatisation)
  - communique directement avec l’Arduino
  - lit les capteurs et actionne la porte

---

## Schéma des Flux de Communication

L’architecture IoT du projet repose sur une **chaîne de communication segmentée**, où chaque maillon assure une fonction critique, de la **détection** jusqu’à l’**actionnement**.

### Smartphone → IA (Vision)

Le smartphone fait office de **caméra IP déportée**.  
Il diffuse un **flux vidéo MJPEG** via le protocole **HTTP** sur le réseau Wi-Fi local.

Le script Python consomme ce flux en continu afin d’effectuer l’analyse visuelle et la reconnaissance faciale.


### IA → Backend (API)

Lorsqu’un visage est **détecté et identifié** avec un **score de confiance suffisant** par le moteur **DeepFace**, le module d’IA transmet le résultat au backend.

Cette communication s’effectue via des **requêtes REST** :
- **Méthode** : `POST`
- **Endpoint** : `/api/detected`


### Backend ↔  Arduino (Hardware)

Cette étape repose sur un **protocole de communication série personnalisé** via **USB**.

- **Lecture des capteurs**  
  Le backend reçoit les données envoyées par l’Arduino (LDR et boutons) au format **JSON**, permettant une interprétation immédiate côté Python.

- **Pilotage des actionneurs**  
  Le backend envoie des **commandes textuelles simples** que l’Arduino décode :
  - `SERVO:Angle` → contrôle de la position de la porte
  - `LCD:Message` → mise à jour de l’affichage LCD

---

## Protocole de Communication (Série)

### Envoi de commandes (Python → Arduino)

Format :
```
DISPOSITIF:VALEUR
```

Exemples :
- `LCD:Bonjour`
- `SERVO:90`

### Réception de données (Arduino → Python)

```json
{"ldr": 45, "b1": 0, "b2": 1, "b3": 0}
```

---

## 🛠️ Sécurité & Logique

### Authentification à deux facteurs
1. Reconnaissance faciale (DeepFace / ArcFace)
2. Code PIN via boutons Arduino

### Gestion de la veille
Activation de l’IA uniquement lors d’une variation détectée par le capteur LDR.

---

## 🚀 Installation et Démarrage

---

### ✅ Prérequis

- **Python 3.10+**
- **Arduino IDE**
- **Smartphone** avec l’application *IP Webcam* (ou équivalent)
- **Matériel** :
  - PC (serveur)
  - Arduino (contrôleur de porte)
  - Servomoteur
  - Écran LCD
  - Boutons poussoirs
  - Capteur LDR

---

### Configuration

Avant le lancement, il est impératif de configurer les **adresses IP** et les **ports série**.

#### Côté IA (`app/config.py`)

- Modifier `CAMERA_IP` avec l’adresse affichée sur votre smartphone
- Ajuster `THRESHOLD` (par défaut `0.30`) pour régler la sensibilité de la reconnaissance faciale

#### Côté Backend (`backend/api/config.py`)

- Modifier `ARDUINO_PORT`  
  Exemple :
  - `/dev/cu.usbmodem1301`
  - `COM3`  
  afin de correspondre au port USB de votre Arduino

---

### ▶️ Lancement du Système

#### 1️⃣ Préparation Arduino

- Ouvrir le fichier :
  ```
  backend/arduino/script_communication/script_communication.ino
  ```
- Téléverser le code sur la carte Arduino via l’IDE Arduino

---

#### 2️⃣ Installation des Dépendances

```bash
pip install -r requirements.txt
```

> **Note** : les dépendances incluent notamment  
> `deepface`, `fastapi`, `pyserial`, `opencv-python`

---

#### 3️⃣ Démarrage du Backend (Gestion Hardware)

```bash
cd backend/api
uvicorn main:app --port 8000 --reload
```

Le backend initialise la **connexion série** avec l’Arduino et attend les signaux de détection.

---

#### 4️⃣ Démarrage de l’Application (IA & Interface Web)

```bash
python app/run.py
```

Le serveur **Flask** démarre par défaut sur le **port 5001** afin d’éviter les conflits système.

---

## 📊 Documentation et Monitoring

- **Interface Utilisateur**  
  http://localhost:5001  
  *(visualisation du flux vidéo en direct)*

- **Documentation API (Swagger)**  
  http://localhost:8000/docs  
  *(tests des endpoints `/api/sensors` et `/api/detected`)*

- **Base de données utilisateurs**  
  Les profils autorisés sont stockés dans :
  ```
  app/ia/data/master_embeddings_db.json
  ```



---

## 👥 Équipe

- Mehdi 
- Enzo 
- Nael 
- Joubrane 
- Amir 

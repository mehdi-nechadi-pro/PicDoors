import requests
import config

def check_ldr_status():
    """Verifie si le capteur LDR detecte une presence (obscurite)"""
    try:
        response = requests.get(config.SENSOR_ENDPOINT, timeout=0.1)
        if response.status_code == 200:
            ldr_value = response.json().get('ldr', 1000)
            return ldr_value < 50 
        return False
    except Exception:
        return False

def send_detection_signal(name):
    """Notifie l'API backend qu'un visage a ete detecte"""
    try:
        print(f"[API] Envoi signal pour : {name}")
        requests.post(config.DETECTED_ENDPOINT, json={"name": name}, timeout=2.0)
    except Exception as e:
        print(f"[API] Erreur d'envoi : {e}")
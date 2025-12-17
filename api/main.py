import serial
import json
import asyncio
import time
from fastapi import FastAPI, HTTPException

from schemas import FaceDetectionDTO

# Importation de nos nouveaux modules
from automation import AutomationService

# --- CONFIGURATION ---
PORT = "/dev/cu.usbmodem1201" 
BAUDRATE = 9600

class ArduinoController:
    def __init__(self, port):
        print(f"🔌 Initialisation matériel sur {port}...")
        try:
            self.ser = serial.Serial(port, BAUDRATE, timeout=1)
            time.sleep(3) 
            self.ser.reset_input_buffer()
            print("✅ Matériel connecté !")
            
            self.running = True
            # Données par défaut compatibles avec notre DTO
            self.sensor_data = {"ldr": 0, "b1": 0, "b2": 0, "b3": 0}
            
        except Exception as e:
            print(f"❌ Erreur connexion matériel : {e}")
            self.ser = None

    def send_command(self, device, value):
        if self.ser:
            cmd = f"{device}:{value}\n"
            self.ser.write(cmd.encode())

    async def read_loop(self):
        """Lit le port série en permanence"""
        while self.running and self.ser:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    try:
                        self.sensor_data = json.loads(line)
                    except json.JSONDecodeError:
                        pass
            except OSError:
                break
            await asyncio.sleep(0.01)

# --- INITIALISATION ---
app = FastAPI(title="Projet IoT Structuré")

# Instances globales
controller = None
automation = None

@app.on_event("startup")
async def startup():
    global controller, automation
    
    # 1. On démarre le contrôleur (Bas niveau)
    controller = ArduinoController(PORT)
    asyncio.create_task(controller.read_loop())
    
    # 2. On démarre l'automatisation (Haut niveau)
    # On lui injecte le contrôleur pour qu'il puisse agir
    automation = AutomationService(controller)
    asyncio.create_task(automation.start_loop())

# --- ENDPOINTS (Pour garder le contrôle manuel si besoin) ---

@app.get("/api/sensors")
def get_sensors():
    return controller.sensor_data

@app.post("/api/lcd")
def force_lcd(message: str):
    # Note : L'automatisation risque d'écraser ce message très vite
    # Dans un vrai projet, il faudrait ajouter une fonction "pause" à l'automation
    controller.send_command("LCD", message)
    return {"status": "envoyé"}


# --- ENDPOINT MODIFIÉ ---
@app.post("/api/detected")
def face_detected(data: FaceDetectionDTO):
    """
    Appelé par la caméra. Lance le mode Authentification.
    """
    print(f"👤 VISAGE RECONNU : {data.name}")
    
    # Au lieu d'ouvrir, on lance la demande de code
    if automation:
        automation.start_authentication(data.name)
        return {"status": "auth_required", "message": "Waiting for PIN"}
    
    return {"error": "Automation not ready"}
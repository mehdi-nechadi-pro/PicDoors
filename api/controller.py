from fastapi import FastAPI
from pyfirmata import Arduino, util
import time

# --- CONFIGURATION ---
PORT_ARDUINO = "/dev/cu.usbmodem1201" 

class ArduinoController:
    def __init__(self, port):
        print(f"🔌 Tentative de connexion à {port}...")
        self.pins = {} # Dictionnaire pour stocker les pins configurées
        try:
            self.board = Arduino(port)
            print("✅ Arduino connecté !")
            
            # Démarrage du thread de lecture
            self.it = util.Iterator(self.board)
            self.it.start()

        except Exception as e:
            print(f"❌ Erreur de connexion : {e}")
            self.board = None

    def set_led(self, pin_id: int, state: bool):
        if not self.board:
             return {"status": "error", "message": "Arduino pas connecté"}

        # Sécurité : on empêche de toucher aux pins 0 et 1 (TX/RX)
        if pin_id < 2:
            return {"status": "error", "message": "Impossible d'utiliser les pins 0 et 1"}

        try:
            # Si on n'a pas encore configuré cette pin, on le fait maintenant
            if pin_id not in self.pins:
                # Configuration dynamique : d = digital, pin_id, o = output
                print(f"⚙️ Configuration de la Pin {pin_id} en OUTPUT")
                self.pins[pin_id] = self.board.get_pin(f'd:{pin_id}:o')

            # Récupération de l'objet pin et écriture
            pin = self.pins[pin_id]
            valeur = 1 if state else 0
            pin.write(valeur)
            
            return {
                "status": "success", 
                "pin": pin_id, 
                "state": "ON" if state else "OFF"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- APPLICATION API ---
app = FastAPI()
controller = None

@app.on_event("startup")
def startup_event():
    global controller
    controller = ArduinoController(PORT_ARDUINO)

@app.post("/led/{id}/{state}")
def switch_led(id: int, state: str):
    """
    Contrôler n'importe quelle LED/Pin.
    Exemple: /led/2/on  ou  /led/13/off
    """
    is_on = (state.lower() == "on")
    # On passe maintenant l'ID et l'état au contrôleur
    return controller.set_led(id, is_on)
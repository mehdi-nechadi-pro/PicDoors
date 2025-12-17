# hardware/arduino_manager.py
from pyfirmata import Arduino, util
import time
import config

class ArduinoController:
    def __init__(self):
        print(f"🔌 Tentative de connexion Arduino sur {config.ARDUINO_PORT}...")
        self.board = None
        self.pins = {}
        
        try:
            self.board = Arduino(config.ARDUINO_PORT)
            print("✅ Arduino connecté via PyFirmata !")
            
            # Démarrage du thread de lecture (important pour ne pas bloquer)
            self.it = util.Iterator(self.board)
            self.it.start()
            
            # Pré-configuration des LEDs (Facultatif mais propre)
            self.pins['green'] = self.board.get_pin(f'd:{config.PIN_LED_VERT}:o')
            self.pins['red'] = self.board.get_pin(f'd:{config.PIN_LED_ROUGE}:o')
            
        except Exception as e:
            print(f"❌ Erreur connexion Arduino : {e}")
            print("⚠️ Le système continuera sans matériel physique.")

    def _set_pin(self, pin_key, state):
        """Méthode interne pour activer une pin"""
        if self.board and pin_key in self.pins:
            self.pins[pin_key].write(1 if state else 0)

    def grant_access(self, user_name):
        """
        Action quand l'utilisateur est reconnu.
        1. Allume LED Verte
        2. (Théorique) Envoie le nom à l'LCD
        """
        print(f"🔓 ARDUINO: Ouverture porte pour {user_name}")
        
        # Action physique
        self._set_pin('green', True)
        self._set_pin('red', False)
        
        # NOTE : Pour l'LCD avec PyFirmata, c'est très complexe.
        # Si vous voulez afficher le texte, il faudra utiliser pyserial pur
        # ou une librairie LCD compatible Firmata.
        
        # On laisse ouvert 3 secondes puis on éteint
        time.sleep(3) 
        self._set_pin('green', False)

    def deny_access(self):
        """Action quand l'utilisateur est inconnu"""
        print("🔒 ARDUINO: Accès refusé")
        self._set_pin('red', True)
        self._set_pin('green', False)
        time.sleep(1)
        self._set_pin('red', False)
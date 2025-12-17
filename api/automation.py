import asyncio
import time
from schemas import SensorDataDTO

# Base de données des codes secrets
USER_CODES = {
    "Joubrane": [1, 3, 2], # Bouton 1, puis 3, puis 2
    "Amir": [2, 1, 3]
}

class AutomationService:
    def __init__(self, controller):
        self.controller = controller
        self.running = False
        
        # --- ETAT DU SYSTÈME ---
        self.mode = "NORMAL" # "NORMAL" (Lumière) ou "AUTH" (Attente code)
        self.current_user_auth = None
        self.input_buffer = [] 
        self.auth_timeout = 0  # Pour annuler si trop long
        
        # --- GESTION DES BOUTONS (Anti-répétition) ---
        self.last_btn_states = [0, 0, 0] # [b1, b2, b3]

    def start_authentication(self, username):
        """Lance la séquence de demande de code"""
        if username not in USER_CODES:
            print(f"Utilisateur {username} inconnu !")
            return

        print(f"🔐 Démarrage auth pour {username}")
        self.mode = "AUTH"
        self.current_user_auth = username
        self.input_buffer = []
        self.auth_timeout = time.time() + 15 # 15 secondes pour taper le code
        
        # Feedback écran
        self.controller.send_command("LCD", f"Salut {username}!")
        time.sleep(1.5)
        self.controller.send_command("LCD", "Entrez Code: _ _ _")

    async def start_loop(self):
        self.running = True
        print("🧠 Cerveau activé.")
        
        while self.running:
            raw_data = self.controller.sensor_data
            try:
                sensors = SensorDataDTO(**raw_data)
                
                # 1. GESTION DES CLICS BOUTONS (Front montant)
                current_btns = [sensors.b1, sensors.b2, sensors.b3]
                clicked_btn = 0
                
                for i in range(3):
                    # Si bouton appuyé (1) ET qu'il était relâché avant (0)
                    if current_btns[i] == 1 and self.last_btn_states[i] == 0:
                        clicked_btn = i + 1 # Bouton 1, 2 ou 3
                    
                self.last_btn_states = current_btns # Mise à jour mémoire

                # 2. LOGIQUE SELON LE MODE
                if self.mode == "AUTH":
                    await self.handle_auth_mode(clicked_btn)
                else:
                    await self.handle_normal_mode(sensors)
                
            except Exception as e:
                pass
            
            await asyncio.sleep(0.05) # Réactivité rapide pour les boutons

    async def handle_auth_mode(self, clicked_btn):
        # A. Vérification Timeout
        if time.time() > self.auth_timeout:
            self.controller.send_command("LCD", "Temps ecoule!")
            time.sleep(2)
            self.mode = "NORMAL"
            return

        # B. Si un bouton a été cliqué
        if clicked_btn > 0:
            print(f"Bouton {clicked_btn} appuyé")
            self.input_buffer.append(clicked_btn)
            
            # Mise à jour visuelle (Ex: "* *")
            stars = "*" * len(self.input_buffer)
            self.controller.send_command("LCD", f"Code: {stars}")

            # C. Vérification du code complet (3 chiffres)
            if len(self.input_buffer) == 3:
                expected_code = USER_CODES.get(self.current_user_auth)
                
                if self.input_buffer == expected_code:
                    await self.access_granted()
                else:
                    await self.access_denied()

    async def access_granted(self):
        print("✅ CODE BON !")
        self.controller.send_command("LCD", "ACCES AUTORISE")
        self.controller.send_command("SERVO", 0) # Ouvre la porte
        
        # On laisse la porte ouverte 5 secondes
        await asyncio.sleep(5)
        
        self.controller.send_command("SERVO", 90) # Ferme
        self.controller.send_command("LCD", "Porte fermee")
        time.sleep(1)
        self.mode = "NORMAL" # Retour gestion lumière

    async def access_denied(self):
        print("❌ CODE FAUX !")
        self.controller.send_command("LCD", "CODE FAUX !")
        time.sleep(2)
        self.input_buffer = [] # On vide pour retenter ? 
        # Ou on quitte direct :
        self.mode = "NORMAL"

    async def handle_normal_mode(self, sensors):
        # Ta logique de lumière existante
        message = ""
        if not sensors.est_sombre: message = f"Personne({sensors.ldr})"
        else: message = f"Presence({sensors.ldr})"
        
        # On envoie (avec anti-spam basique géré par le controller si besoin)
        # Ici on simplifie
        self.controller.send_command("LCD", message)
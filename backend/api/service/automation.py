import asyncio
import time
from dto.schemas import SensorDataDTO
from data.codes import USER_CODES

class AutomationService:
    def __init__(self, controller):
        self.controller = controller
        self.running = False
        
        self.mode = "NORMAL"
        self.current_user_auth = None
        self.input_buffer = [] 
        self.auth_timeout = 0
        
        self.last_btn_states = [0, 0, 0]

    def start_authentication(self, username):
        if username not in USER_CODES:
            print(f"Utilisateur {username} inconnu")
            return

        print(f"Demarrage auth pour {username}")
        self.mode = "AUTH"
        self.current_user_auth = username
        self.input_buffer = []
        self.auth_timeout = time.time() + 15
        
        self.controller.send_command("LCD", f"Salut {username}!")
        time.sleep(1.5)
        self.controller.send_command("LCD", "Entrez Code: _ _ _")

    async def start_loop(self):
        self.running = True
        print("Service Automation active")
        
        while self.running:
            raw_data = self.controller.sensor_data
            try:
                sensors = SensorDataDTO(**raw_data)
                
                current_btns = [sensors.b1, sensors.b2, sensors.b3]
                clicked_btn = 0
                
                for i in range(3):
                    if current_btns[i] == 1 and self.last_btn_states[i] == 0:
                        clicked_btn = i + 1
                    
                self.last_btn_states = current_btns

                if self.mode == "AUTH":
                    await self.handle_auth_mode(clicked_btn)
                else:
                    await self.handle_normal_mode(sensors)
                
            except Exception:
                pass
            
            await asyncio.sleep(0.05)

    async def handle_auth_mode(self, clicked_btn):
        if time.time() > self.auth_timeout:
            self.controller.send_command("LCD", "Temps ecoule!")
            time.sleep(2)
            self.mode = "NORMAL"
            return

        if clicked_btn > 0:
            print(f"Bouton {clicked_btn} appuye")
            self.input_buffer.append(clicked_btn)
            
            stars = "*" * len(self.input_buffer)
            self.controller.send_command("LCD", f"Code: {stars}")

            if len(self.input_buffer) == 3:
                expected_code = USER_CODES.get(self.current_user_auth)
                
                if self.input_buffer == expected_code:
                    await self.access_granted()
                else:
                    await self.access_denied()

    async def access_granted(self):
        print("Code Correct")
        self.controller.send_command("LCD", "ACCES AUTORISE")
        self.controller.send_command("SERVO", 0)
        
        await asyncio.sleep(5)
        
        self.controller.send_command("SERVO", 90)
        self.controller.send_command("LCD", "Porte fermee")
        time.sleep(1)
        self.mode = "NORMAL"

    async def access_denied(self):
        print("Code Incorrect")
        self.controller.send_command("LCD", "CODE FAUX !")
        time.sleep(2)
        self.mode = "NORMAL"

    async def handle_normal_mode(self, sensors):
        message = ""
        if not sensors.est_sombre:
            message = f"Personne({sensors.ldr})"
        else:
            message = f"Presence({sensors.ldr})"
        
        self.controller.send_command("LCD", message)
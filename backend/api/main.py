import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request

from dto.schemas import FaceDetectionDTO
from service.serial_service import ArduinoService
from service.automation import AutomationService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application (Démarrage et Arrêt)"""
    
    # Instanciation et connexion au matériel
    arduino = ArduinoService()
    connected = arduino.connect()
    app.state.arduino = arduino
    
    tasks = []
    
    # Si l'Arduino est connecté, on lance les services d'automatisation
    if connected:
        read_task = asyncio.create_task(arduino.read_loop())
        tasks.append(read_task)
        
        automation = AutomationService(arduino)
        app.state.automation = automation
        
        auto_task = asyncio.create_task(automation.start_loop())
        tasks.append(auto_task)
    else:
        app.state.automation = None

    yield # L'application tourne ici

    # Nettoyage à l'arrêt de l'application
    arduino.close()
    
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(title="PicDoors Backend", lifespan=lifespan)

# --- ROUTES ---

@app.get("/api/sensors")
def get_sensors(request: Request):
    """Récupère les dernières données des capteurs"""
    if not request.app.state.arduino:
        raise HTTPException(status_code=503, detail="Arduino non connecté")
    
    return request.app.state.arduino.sensor_data

@app.post("/api/detected")
def face_detected(data: FaceDetectionDTO, request: Request):
    """Appelé par l'IA pour déclencher la demande de code PIN"""
    automation = getattr(request.app.state, 'automation', None)
    
    if not automation:
        raise HTTPException(status_code=503, detail="Automation non démarrée")

    automation.start_authentication(data.name)
    
    return {"status": "auth_initiated", "target": data.name}
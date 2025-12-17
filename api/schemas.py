from pydantic import BaseModel

class SensorDataDTO(BaseModel):
    ldr: int
    b1: bool
    b2: bool
    b3: bool

    # On peut ajouter des propriétés calculées (helper)
    @property
    def est_sombre(self) -> bool:
        return self.ldr < 70
    
class FaceDetectionDTO(BaseModel):
    name: str
    



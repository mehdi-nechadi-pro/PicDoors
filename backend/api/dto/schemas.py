from pydantic import BaseModel

class SensorDataDTO(BaseModel):
    ldr: int
    b1: bool
    b2: bool
    b3: bool

    @property
    def est_sombre(self) -> bool:
        return self.ldr < 50
    
class FaceDetectionDTO(BaseModel):
    name: str
    



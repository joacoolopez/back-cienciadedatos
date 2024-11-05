from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str



class PredictionCardiacoInput(BaseModel):
    Age: float
    BMI: float
    HbA1cLevel: float
    BloodGlucoseLevel: float

class PredictionDiabetesInput(BaseModel):
    GenHlth: int
    HighBP: int
    BMI: float
    DiffWalk: int
    HighChol: int
    Age: int
    HeartDiseaseorAttack: int
    PhysHlth: int
    Income: int
    Education: int
    ultimo_ano_al_medico: bool 

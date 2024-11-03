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
    HighBP: int
    HighChol: int
    CholCheck: int
    BMI: float
    Smoker: int
    Stroke: int
    HeartDiseaseorAttack: int
    PhysActivity: int
    Fruits: int
    Veggies: int
    HvyAlcoholConsump: int
    AnyHealthcare: int
    NoDocbcCost: int
    GenHlth: int
    MentHlth: int
    PhysHlth: int
    DiffWalk: int
    Sex: int
    Age: int
    Education: int
    Income: int

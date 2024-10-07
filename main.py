from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

model = joblib.load('modelo_joblib1.pkl')

class PredictionInput(BaseModel):
    Age: int
    BMI: float
    Smoker: bool
    Fruits: bool
    Veggies: bool


@app.post("/predict")
def predict(input_data: PredictionInput):
    try:
        data = np.array([[input_data.Age, input_data.BMI, input_data.Smoker, input_data.Fruits, input_data.Veggies]])
        prediction_proba = model.predict_proba(data)[0]
        return {
        "probabilidad_de_no_diabetes": f"{prediction_proba[0]:.2f}",
        "probabilidad_de_diabetes": f"{prediction_proba[1]:.2f}"
    }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción: {str(e)}")



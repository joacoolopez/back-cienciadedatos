from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()


# Cargar el modelo de regresión logística
modelo_diabetes = joblib.load('modelo_diabetes_logreg.pkl')
modelo_cardiaco = joblib.load('modelo_random_forest_diabetes.pkl')

# Definir el modelo de entrada
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

class PredictionCardiacoInput(BaseModel):
    Age: float
    BMI: float
    HbA1cLevel: float
    BloodGlucoseLevel: float

@app.post("/predict-diabetes")
def predictDiabetes(input_data: PredictionDiabetesInput):
    try:
        
        input_data_df = pd.DataFrame([input_data.dict()])

        input_data_df['Diabetes_012'] = 0  

        columnas_modelo = ['Diabetes_012', 'GenHlth', 'HighBP', 'BMI', 'DiffWalk', 
                            'HighChol', 'Age', 'HeartDiseaseorAttack', 'PhysHlth', 'Income']

        input_data_df = input_data_df[columnas_modelo]
        

        probabilidad_diabetes = modelo_diabetes.predict_proba(input_data_df)[:, 1]
        

        return {"probabilidad_diabetes": probabilidad_diabetes[0]}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción: {str(e)}")

@app.post("/predict-cardiaco")
def predictCardiaco(input_data: PredictionCardiacoInput):
    try:
        input_df = pd.DataFrame([input_data.dict()])
        
        columnas_modelo = ['age', 'bmi', 'HbA1c_level', 'blood_glucose_level']

        input_df.columns = columnas_modelo
        
        probabilidad = modelo_cardiaco.predict_proba(input_df)[:, 1]  

        return {"probabilidad_cardiaco": probabilidad[0]}
        

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción: {str(e)}")
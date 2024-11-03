import os
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
from dotenv import load_dotenv
import joblib
import pandas as pd
from models import User, UserResponse, PredictionDiabetesInput, PredictionCardiacoInput
from utils import hash_password, verify_password, create_access_token

load_dotenv()

# Configuración de variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI()

# Configuración de MongoDB
client = MongoClient(MONGO_URI)
db = client["CienciaDeDatos"]
users_collection = db["users"]
historial_collection = db["historial_diabetes"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

modelo_diabetes = joblib.load('./ml_models/modelo_diabetes_rf.pkl')
modelo_cardiaco = joblib.load('./ml_models/modelo_random_forest_diabetes.pkl')

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/register", response_model=UserResponse)
def register(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = hash_password(user.password)
    user_data = {"username": user.username, "password": hashed_password}
    result = users_collection.insert_one(user_data)
    
    return {"id": str(result.inserted_id), "username": user.username}

@app.post("/login")
def login(user: User):
    db_user = users_collection.find_one({"username": user.username})
    
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    # Crear un token JWT
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/usuarios/me")
def read_users_me(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Get the token from the Bearer header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"username": username}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


@app.post("/predict-diabetes")
def predictDiabetes(input_data: PredictionDiabetesInput, username: str = Depends(read_users_me)):
    try:
        # Convertir la entrada a DataFrame
        input_data_df = pd.DataFrame([input_data.dict()])
        
        # Añadir la columna 'Diabetes_012' inicializada a 0
        input_data_df['Diabetes_012'] = 0

        # Definir las columnas del modelo
        columnas_modelo = [
            'HighBP',
            'HighChol',
            'CholCheck',
            'BMI',
            'Smoker',
            'Stroke',
            'HeartDiseaseorAttack',
            'PhysActivity',
            'Fruits',
            'Veggies',
            'HvyAlcoholConsump',
            'AnyHealthcare',
            'NoDocbcCost',
            'GenHlth',
            'MentHlth',
            'PhysHlth',
            'DiffWalk',
            'Sex',
            'Age',
            'Education',
            'Income'
        ]

        input_data_df = input_data_df[columnas_modelo]
        
        probabilidad_diabetes = modelo_diabetes.predict_proba(input_data_df)[:, 1]
        

        resultado_diabetes = "positivo" if probabilidad_diabetes[0] > 0.5 else "negativo"

        historial_data = {
            "username": username["username"],
            "resultado": resultado_diabetes,
            "probabilidad": probabilidad_diabetes[0],
            "fecha": datetime.utcnow()
        }
        
        historial_collection.insert_one(historial_data)

        return {"probabilidad_diabetes": probabilidad_diabetes[0], "resultado": resultado_diabetes}

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
    
@app.get("/historial")
def get_historial():
    try:
        historial = list(historial_collection.find())
        for entry in historial:
            entry["_id"] = str(entry["_id"])  # Convertir el ObjectId a string para su visualización
        return historial
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener el historial: {str(e)}")
    

@app.get("/historial-usuario")
def get_historial_usuario(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Obtener el token del encabezado Bearer
    try:
        # Decodificar el token para obtener el nombre de usuario
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Obtener el historial del usuario
        historial = list(historial_collection.find({"username": username}))
        for entry in historial:
            entry["_id"] = str(entry["_id"])  # Convertir el ObjectId a string para su visualización
        return historial

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener el historial de {username}: {str(e)}")

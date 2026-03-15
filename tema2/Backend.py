import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from UserAPI import USER_CODES
from models import UserRequest, GradeRequest

app = FastAPI()

# pentru ca Reactul(front) sa poata comunica cu back-ul
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

CATALOG_API = "http://localhost:8000"
CATALOG_CODES = {
    400: "Resursele oferite nu sunt bune",
    404: "Nu s-a gasit stuent/nota in baza de date",
    405: "Nu poti modifica toate inregistrarile",
    409: "Studentul deja are nota la aceasta materie",
    500: "Eroare la server"
}

USER_API= "http://localhost:8002"

load_dotenv()
API_KEY=os.getenv("api_key")

@app.get("/catalog/{id_student}/{materie}")
async def getGrade(id_student: int, materie: str):
    async with httpx.AsyncClient() as client:
        # luam numele
        try:
            response = await client.get(
                f"{CATALOG_API}/student/{id_student}"
            )
            response_code = response.status_code
            if response_code >= 400:
                raise HTTPException(
                    status_code=response_code,
                    detail=CATALOG_CODES[response_code])
            student_name = response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Catalog offline")

        # luam nota

        try:
            response = await client.get(
                f"{CATALOG_API}/note/{id_student}/{materie}"
            )
            response_code = response.status_code
            if response_code >= 400:
                raise HTTPException(
                    status_code=response_code,
                    detail=CATALOG_CODES[response_code]
                )
            student_grade = response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Catalog offline")

        return {
            "id": id_student,
            "nume": student_name[0],
            "prenume": student_name[1],
            "materie": student_grade[1],
            "nota": student_grade[2]
        }


@app.post("/catalog/nota")
async def setGrade(request: GradeRequest):
    async with httpx.AsyncClient() as client:
        payload=[{
            "studentId":request.id_student,
            "materie":request.materie,
            "nota":request.nota
        }]

        try:
            response= await client.post(
                url=f"{CATALOG_API}/note",
                json=payload
            )
            response_code=response.status_code
            if response_code >= 400:
                raise HTTPException(status_code=response_code, detail=CATALOG_CODES[response_code])
            return {"message": "Nota adaugata cu succes!"}
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Catalog offline")

@app.put("/catalog/nota")
async def setGrade(request: GradeRequest):
    async with httpx.AsyncClient() as client:
        payload={
            "studentId":request.id_student,
            "materie":request.materie,
            "nota":request.nota
        }

        try:
            response= await client.put(
                url=f"{CATALOG_API}/note/{payload['studentId']}/{payload['materie']}/{payload['nota']}",
            )
            response_code=response.status_code
            if response_code >= 400:
                raise HTTPException(status_code=response_code, detail=CATALOG_CODES[response_code])
            return {"message": "Nota actualizata cu succes!"}
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Catalog offline")


@app.post("/register")
async def register(request: UserRequest):
    async with httpx.AsyncClient() as client:
        payload={
            "username":request.username,
            "password":request.password
        }

        try:
            response= await client.post(
                url=f"{USER_API}/register",
                json=payload
            )
            response_code=response.status_code
            if response_code >= 400:
                raise HTTPException(status_code=response_code, detail=USER_CODES[response_code])
            return {"message": "Inregistrat cu succes!"}
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User manager offline")

@app.post("/login")
async def login(request: UserRequest):
    async with httpx.AsyncClient() as client:
        payload={
            "username":request.username,
            "password":request.password
        }

        try:
            response= await client.post(
                url=f"{USER_API}/login",
                json=payload
            )
            response_code=response.status_code
            if response_code >= 400:
                raise HTTPException(status_code=response_code, detail=USER_CODES[response_code])
            return {"message": "Logat cu succes!"}
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User manager offline")


@app.get("/weather/{city}")
async def getWeather(city:str):
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        try:
            response= await client.get(url)
            response_code=response.status_code
            if response_code>=400:
                raise HTTPException(status_code=response_code, detail="Problema la serviciul meteo extern")

            data=response.json()
            return{
                "oras":city,
                "temperatura":data['main']['temp'],
                "conditii":data['weather'][0]['description'],
                "icon":data["weather"][0]['icon']
            }

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Serviciul meteo este offline")


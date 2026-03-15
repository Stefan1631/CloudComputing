import httpx
import passlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.handlers.bcrypt import bcrypt

from pydantic import BaseModel
from passlib.context import CryptContext

from dbService import getPassword, addUser
from models import UserRequest


app = FastAPI()
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

# pentru ca Reactul(front) sa poata comunica cu back-ul
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

USER_CODES={
    400:"Parola gresita",
    404:"Nu exista user-ul",
    500:"Eroare la server"
}

@app.post("/register")
async def register(request: UserRequest):
    async with httpx.AsyncClient() as client:
        username=request.username
        password=request.password
        password=pwd_context.hash(password)
        try:
            response_code=201
            response=addUser(username,password)
            if response==-1:
                response_code=500

            if response_code >= 400:
                raise HTTPException(status_code=response_code, detail=USER_CODES[response_code])
            return {"message": "Inregistrat cu succes!"}
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User manager offline")

@app.post("/login")
async  def login(request : UserRequest):
    async with httpx.AsyncClient() as client:
        username=request.username
        givenPassword=request.password

        try:
            response_code=200
            password=getPassword(username)
            if password==None:
                response_code=404
            elif password==-1:
                response_code=500
            elif not pwd_context.verify(givenPassword,password):
                response_code=400
            if response_code >= 400:
                raise HTTPException(status_code=response_code, detail=USER_CODES[response_code])
            return {"message": "Logat cu succes!"}
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User manager offline")


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from app.core.config import settings

router = APIRouter()
users_db = {}

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

def create_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": email, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode()[:72], hashed.encode())

@router.post("/register")
async def register(body: RegisterRequest):
    if body.email in users_db:
        raise HTTPException(status_code=400, detail="Email already exists")
    users_db[body.email] = {
        "name": body.name,
        "password": hash_password(body.password)
    }
    return {"access_token": create_token(body.email), "token_type": "bearer"}

@router.post("/login")
async def login(body: LoginRequest):
    user = users_db.get(body.email)
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(body.email), "token_type": "bearer"}
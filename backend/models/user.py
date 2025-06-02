from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    
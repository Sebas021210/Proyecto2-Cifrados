from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

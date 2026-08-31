from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

class Token(BaseModel):
    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = "bearer"

class TokenPair(BaseModel):
    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de atualização JWT")
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="Token de atualização JWT")
    token_type: str = "bearer"
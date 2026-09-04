from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=8, description="Senha do usuário")


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50, description="Nome de usuário")
    email: EmailStr | None = Field(None, description="Email do usuário")
    password: str | None = Field(None, min_length=8, description="Senha do usuário")


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)


from pydantic import BaseModel, Field


class UserRegisterDTO(BaseModel):
    """
    DTO para registro de usuario (username + password en claro).
    """
    username: str = Field(..., description="Nombre de usuario único")
    password: str = Field(..., min_length=6, description="Contraseña en claro")
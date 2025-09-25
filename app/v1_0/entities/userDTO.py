from pydantic import BaseModel, Field
from datetime import datetime

class UserDTO(BaseModel):
    """
    DTO para la entidad Usuario.
    """
    username: str = Field(..., description="Nombre de usuario único")
    hashed_password: str = Field(..., description="Contraseña ya hasheada")
    is_active: bool = Field(True, description="Flag que indica si la cuenta está activa")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación del usuario")
from pydantic import BaseModel


# =========================
# CONNECTIONS
# =========================

class ConnectionCreate(BaseModel):

    nombre: str

    motor: str

    host: str

    port: int

    database_name: str

    user_name: str

    status: str


# =========================
# AUTH
# =========================

class UserLogin(BaseModel):

    username: str

    password: str
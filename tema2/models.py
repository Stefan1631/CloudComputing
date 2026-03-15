from pydantic import BaseModel


class GradeRequest(BaseModel):
    id_student: int
    materie: str
    nota: int


class UserRequest(BaseModel):
    username: str
    password: str

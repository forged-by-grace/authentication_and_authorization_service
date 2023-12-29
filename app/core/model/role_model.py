from pydantic import BaseModel

class Role(BaseModel):
    name: str
    permissions: list[str] = []
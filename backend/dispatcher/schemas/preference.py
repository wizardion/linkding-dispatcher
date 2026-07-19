from pydantic import BaseModel


class UserPreference(BaseModel):
    tags: list[str] = []
    bundle: str = ""
    archived: bool = False
    remember: bool = False

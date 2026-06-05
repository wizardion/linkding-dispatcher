from pydantic import BaseModel


class SaveRequest(BaseModel):
    url: str
    tags: list[str]
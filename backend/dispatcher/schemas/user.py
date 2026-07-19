from pydantic import BaseModel, ConfigDict
from starlette.authentication import SimpleUser


class AuthUser(BaseModel, SimpleUser):
    """User object to store extra token payload data if needed."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    token: str

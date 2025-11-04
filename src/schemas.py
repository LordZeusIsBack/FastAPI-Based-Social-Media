from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from fastapi_users import schemas


class PostResponse(BaseModel):
    id: UUID
    caption: str | None = None
    url: str
    file_type: str
    file_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class UserRead(schemas.BaseUser[UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass

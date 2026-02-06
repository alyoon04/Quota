import uuid
from datetime import datetime

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    default_rpm: int


class PlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    default_rpm: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreate(BaseModel):
    label: str
    plan_id: uuid.UUID


class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    label: str
    plan_id: uuid.UUID
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(ApiKeyResponse):
    plaintext_key: str

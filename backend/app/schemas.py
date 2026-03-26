import uuid
from datetime import datetime

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    default_rpm: int


class PlanUpdate(BaseModel):
    name: str | None = None
    default_rpm: int | None = None


class PlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    default_rpm: int
    created_at: datetime
    key_count: int = 0

    model_config = {"from_attributes": True}


class ApiKeyCreate(BaseModel):
    label: str
    plan_id: uuid.UUID


class ApiKeyUpdate(BaseModel):
    is_active: bool


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


class StatsResponse(BaseModel):
    total_plans: int
    total_keys: int
    requests_today: int


class UserCreate(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_admin
from app.models import ApiKey, Plan
from app.schemas import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    PlanCreate,
    PlanResponse,
    PlanUpdate,
)

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])


@router.post("/plans", response_model=PlanResponse, status_code=201)
async def create_plan(body: PlanCreate, db: AsyncSession = Depends(get_db)):
    plan = Plan(
        id=uuid.uuid4(),
        name=body.name,
        default_rpm=body.default_rpm,
        created_at=datetime.now(timezone.utc),
    )
    db.add(plan)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Plan name already exists")
    await db.refresh(plan)
    return plan


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).order_by(Plan.created_at))
    return result.scalars().all()


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    plan = await db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.patch("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: uuid.UUID, body: PlanUpdate, db: AsyncSession = Depends(get_db)
):
    plan = await db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if body.name is not None:
        plan.name = body.name
    if body.default_rpm is not None:
        plan.default_rpm = body.default_rpm
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Plan name already exists")
    await db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    plan = await db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    # Reject if API keys still reference this plan
    result = await db.execute(
        select(ApiKey).where(ApiKey.plan_id == plan_id).limit(1)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=409,
            detail="Cannot delete plan with existing API keys",
        )
    await db.delete(plan)
    await db.commit()


@router.post("/api-keys", response_model=ApiKeyCreatedResponse, status_code=201)
async def create_api_key(body: ApiKeyCreate, db: AsyncSession = Depends(get_db)):
    # Verify plan exists
    plan = await db.get(Plan, body.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    plaintext_key = secrets.token_hex(16)
    key_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()

    api_key = ApiKey(
        id=uuid.uuid4(),
        key_hash=key_hash,
        label=body.label,
        plan_id=body.plan_id,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyCreatedResponse(
        id=api_key.id,
        label=api_key.label,
        plan_id=api_key.plan_id,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        plaintext_key=plaintext_key,
    )


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey).order_by(ApiKey.created_at))
    return result.scalars().all()

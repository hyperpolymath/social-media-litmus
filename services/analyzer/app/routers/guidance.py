"""Guidance generation endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
from datetime import datetime

from app.database import get_session, GuidanceDraft, PolicyChange
from app.nlp.analyzer import analyzer
from pydantic import BaseModel

router = APIRouter()


class GuidanceRequest(BaseModel):
    """Request to generate guidance"""
    change_ids: List[UUID]
    platform_name: str
    draft_type: str = "regular"


class GuidanceResponse(BaseModel):
    """Generated guidance"""
    draft_id: UUID
    title: str
    summary: str
    content: str
    status: str


@router.post("/generate", response_model=GuidanceResponse)
async def generate_guidance(
    request: GuidanceRequest,
    session: AsyncSession = Depends(get_session),
):
    """Generate member guidance from policy changes"""
    # Fetch changes
    result = await session.execute(
        select(PolicyChange).where(PolicyChange.id.in_(request.change_ids))
    )
    changes = result.scalars().all()

    if not changes:
        raise HTTPException(status_code=404, detail="No changes found")

    # Generate guidance
    changes_data = [
        {
            "id": str(c.id),
            "change_summary": c.change_summary,
            "severity": c.severity,
            "impact_assessment": c.impact_assessment,
        }
        for c in changes
    ]

    guidance = await analyzer.generate_guidance(
        changes=changes_data,
        platform_name=request.platform_name,
    )

    # Create draft
    draft = GuidanceDraft(
        title=guidance["title"],
        summary=guidance["summary"],
        content_markdown=guidance["content_markdown"],
        draft_type=request.draft_type,
        status="draft",
        related_changes=[str(c.id) for c in changes],
        generated_by="ai",
        ai_model="gpt-4",
        drafted_by="analyzer-service",
        drafted_at=datetime.utcnow(),
    )

    session.add(draft)
    await session.commit()
    await session.refresh(draft)

    return GuidanceResponse(
        draft_id=draft.id,
        title=draft.title,
        summary=draft.summary or "",
        content=draft.content_markdown,
        status=draft.status,
    )


@router.get("/drafts")
async def list_drafts(
    status: str = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    """List guidance drafts"""
    query = select(GuidanceDraft)

    if status:
        query = query.where(GuidanceDraft.status == status)

    query = query.order_by(GuidanceDraft.drafted_at.desc()).limit(limit)

    result = await session.execute(query)
    drafts = result.scalars().all()

    return {
        "drafts": [
            {
                "id": str(draft.id),
                "title": draft.title,
                "status": draft.status,
                "drafted_at": draft.drafted_at.isoformat(),
                "generated_by": draft.generated_by,
            }
            for draft in drafts
        ],
        "count": len(drafts),
    }


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get specific guidance draft"""
    result = await session.execute(
        select(GuidanceDraft).where(GuidanceDraft.id == draft_id)
    )
    draft = result.scalar_one_or_none()

    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    return {
        "id": str(draft.id),
        "title": draft.title,
        "summary": draft.summary,
        "content": draft.content_markdown,
        "status": draft.status,
        "draft_type": draft.draft_type,
        "related_changes": draft.related_changes,
        "generated_by": draft.generated_by,
        "drafted_at": draft.drafted_at.isoformat(),
    }

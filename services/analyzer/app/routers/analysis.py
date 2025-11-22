"""Analysis endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database import get_session, PolicyChange, NLPAnalysis
from app.nlp.analyzer import analyzer
from pydantic import BaseModel

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request to analyze a policy change"""
    change_id: UUID
    force_reanalysis: bool = False


class AnalysisResponse(BaseModel):
    """Analysis result"""
    change_id: UUID
    severity: str
    confidence: float
    summary: str
    impact: str
    requires_notification: bool


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_change(
    request: AnalysisRequest,
    session: AsyncSession = Depends(get_session),
):
    """Analyze a specific policy change"""
    # Fetch the change
    result = await session.execute(
        select(PolicyChange).where(PolicyChange.id == request.change_id)
    )
    change = result.scalar_one_or_none()

    if not change:
        raise HTTPException(status_code=404, detail="Change not found")

    # Check if already analyzed (unless force reanalysis)
    if not request.force_reanalysis:
        existing = await session.execute(
            select(NLPAnalysis).where(
                NLPAnalysis.policy_change_id == change.id
            ).limit(1)
        )
        if existing.scalar_one_or_none():
            return AnalysisResponse(
                change_id=change.id,
                severity=change.severity,
                confidence=float(change.confidence_score),
                summary=change.change_summary or "",
                impact=change.impact_assessment or "",
                requires_notification=change.requires_member_notification,
            )

    # Perform analysis
    # Note: In production, this would fetch actual snapshot content
    analysis = await analyzer.analyze_change(
        previous_content="Previous policy content...",
        current_content="Current policy content...",
        platform_name="Platform",
        document_type="policy",
    )

    # Update change record
    change.severity = analysis["severity"]
    change.confidence_score = analysis["confidence"]
    change.change_summary = analysis["change_summary"]
    change.impact_assessment = analysis["impact_assessment"]
    change.requires_member_notification = analysis["requires_notification"]
    change.affected_sections = analysis["affected_sections"]

    await session.commit()

    # Store NLP analysis
    nlp_analysis = NLPAnalysis(
        policy_change_id=change.id,
        detected_at=change.detected_at,
        analysis_type="comprehensive",
        model_name=analyzer.client.model or "gpt-4",
        result=analysis,
        confidence_score=analysis["confidence"],
    )
    session.add(nlp_analysis)
    await session.commit()

    return AnalysisResponse(
        change_id=change.id,
        severity=analysis["severity"],
        confidence=analysis["confidence"],
        summary=analysis["change_summary"],
        impact=analysis["impact_assessment"],
        requires_notification=analysis["requires_notification"],
    )


@router.get("/changes/unanalyzed")
async def get_unanalyzed_changes(
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    """Get policy changes that haven't been analyzed yet"""
    result = await session.execute(
        select(PolicyChange)
        .where(PolicyChange.severity == "unknown")
        .where(PolicyChange.false_positive == False)
        .limit(limit)
    )
    changes = result.scalars().all()

    return {
        "changes": [
            {
                "id": str(change.id),
                "detected_at": change.detected_at.isoformat(),
                "change_type": change.change_type,
            }
            for change in changes
        ],
        "count": len(changes),
    }

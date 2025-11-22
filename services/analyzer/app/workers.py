"""Background workers for continuous analysis"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select

from app.database import async_session_maker, PolicyChange
from app.nlp.analyzer import analyzer

logger = logging.getLogger(__name__)


async def analysis_worker():
    """Continuously analyze unanalyzed policy changes"""
    logger.info("Starting analysis worker")

    await analyzer.initialize()

    while True:
        try:
            async with async_session_maker() as session:
                # Find unanalyzed changes
                result = await session.execute(
                    select(PolicyChange)
                    .where(PolicyChange.severity == "unknown")
                    .where(PolicyChange.false_positive == False)
                    .limit(10)
                )
                changes = result.scalars().all()

                if not changes:
                    await asyncio.sleep(30)  # Wait 30s if no work
                    continue

                logger.info(f"Found {len(changes)} changes to analyze")

                for change in changes:
                    try:
                        # In production, fetch actual snapshot content
                        analysis = await analyzer.analyze_change(
                            previous_content="Previous...",
                            current_content="Current...",
                            platform_name="Platform",
                            document_type="policy",
                        )

                        # Update change record
                        change.severity = analysis["severity"]
                        change.confidence_score = analysis["confidence"]
                        change.change_summary = analysis["change_summary"]
                        change.impact_assessment = analysis["impact_assessment"]
                        change.requires_member_notification = analysis["requires_notification"]

                        await session.commit()
                        logger.info(f"Analyzed change {change.id}: {analysis['severity']}")

                    except Exception as e:
                        logger.error(f"Failed to analyze change {change.id}: {e}")
                        await session.rollback()
                        continue

                await asyncio.sleep(5)  # Brief pause between batches

        except Exception as e:
            logger.error(f"Analysis worker error: {e}")
            await asyncio.sleep(60)  # Wait 1 min on error


async def start_workers():
    """Start all background workers"""
    tasks = [
        asyncio.create_task(analysis_worker()),
    ]

    logger.info(f"Started {len(tasks)} background workers")
    return tasks

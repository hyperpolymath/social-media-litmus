"""NLP analysis engine for policy changes"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import difflib

import spacy
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class PolicyAnalyzer:
    """Analyzes policy changes using NLP and AI"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.nlp = None  # Lazy load spaCy

    async def initialize(self):
        """Initialize NLP models"""
        logger.info(f"Loading spaCy model: {settings.spacy_model}")
        self.nlp = spacy.load(settings.spacy_model)
        logger.info("NLP models loaded successfully")

    async def analyze_change(
        self,
        previous_content: str,
        current_content: str,
        platform_name: str,
        document_type: str,
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of policy change

        Returns:
            {
                "severity": "critical|high|medium|low",
                "confidence": 0.0-1.0,
                "change_summary": "...",
                "impact_assessment": "...",
                "affected_sections": [...],
                "requires_notification": bool,
                "key_changes": [...],
                "sentiment_shift": {...},
            }
        """
        logger.info(f"Analyzing change for {platform_name} {document_type}")

        # Run analyses in parallel
        results = await asyncio.gather(
            self._detect_changes(previous_content, current_content),
            self._assess_severity(previous_content, current_content, platform_name),
            self._extract_sections(previous_content, current_content),
            self._analyze_sentiment(previous_content, current_content),
        )

        changes, severity_assessment, sections, sentiment = results

        # Combine results
        analysis = {
            "severity": severity_assessment["severity"],
            "confidence": severity_assessment["confidence"],
            "change_summary": severity_assessment["summary"],
            "impact_assessment": severity_assessment["impact"],
            "affected_sections": sections,
            "requires_notification": severity_assessment["severity"] in ["critical", "high"],
            "key_changes": changes,
            "sentiment_shift": sentiment,
        }

        logger.info(f"Analysis complete: {analysis['severity']} severity")
        return analysis

    async def _detect_changes(
        self, previous: str, current: str
    ) -> List[Dict[str, str]]:
        """Detect specific changes using diff"""
        differ = difflib.Differ()
        diff = list(differ.compare(previous.splitlines(), current.splitlines()))

        changes = []
        for i, line in enumerate(diff):
            if line.startswith("+ "):
                changes.append({
                    "type": "addition",
                    "content": line[2:],
                    "line": i,
                })
            elif line.startswith("- "):
                changes.append({
                    "type": "deletion",
                    "content": line[2:],
                    "line": i,
                })

        return changes[:50]  # Limit to top 50 changes

    async def _assess_severity(
        self, previous: str, current: str, platform_name: str
    ) -> Dict[str, Any]:
        """Use GPT-4 to assess severity and impact"""
        prompt = f"""Analyze this policy change for {platform_name}.

Previous version (excerpt):
{previous[:2000]}

Current version (excerpt):
{current[:2000]}

Assess:
1. Severity (critical/high/medium/low)
2. Impact on journalists and content creators
3. Key changes that matter
4. Whether NUJ members need immediate notification

Respond in JSON format:
{{
    "severity": "critical|high|medium|low",
    "confidence": 0.0-1.0,
    "summary": "Brief summary of changes",
    "impact": "How this affects journalists",
    "key_points": ["point 1", "point 2", ...]
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in social media policy analysis for journalists.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"GPT-4 analysis failed: {e}")
            return {
                "severity": "unknown",
                "confidence": 0.0,
                "summary": "Analysis failed",
                "impact": "Unable to assess",
                "key_points": [],
            }

    async def _extract_sections(
        self, previous: str, current: str
    ) -> List[str]:
        """Extract affected sections/headings"""
        if not self.nlp:
            await self.initialize()

        doc_prev = self.nlp(previous[:100000])  # Limit size
        doc_curr = self.nlp(current[:100000])

        # Simple heading detection (lines ending with :)
        sections = []
        for line in current.splitlines():
            if line.strip().endswith(":") and len(line) < 100:
                sections.append(line.strip())

        return sections[:20]  # Limit to 20 sections

    async def _analyze_sentiment(
        self, previous: str, current: str
    ) -> Dict[str, Any]:
        """Analyze sentiment shift"""
        # Placeholder - would use proper sentiment analysis
        return {
            "previous_tone": "neutral",
            "current_tone": "neutral",
            "shift": "no_change",
            "confidence": 0.5,
        }

    async def generate_guidance(
        self,
        changes: List[Dict[str, Any]],
        platform_name: str,
    ) -> Dict[str, str]:
        """Generate member guidance based on changes"""
        logger.info(f"Generating guidance for {platform_name}")

        # Prepare change summary
        changes_text = "\n".join([
            f"- {c.get('change_summary', 'Policy change detected')}"
            for c in changes[:10]
        ])

        prompt = f"""Write member guidance for NUJ journalists about recent {platform_name} policy changes.

Changes detected:
{changes_text}

Create:
1. A clear title
2. A brief summary (2-3 sentences)
3. Detailed guidance (3-5 paragraphs) covering:
   - What changed
   - Why it matters to journalists
   - Practical recommendations
   - What to watch for

Tone: Professional, clear, actionable
Audience: Working journalists and content creators

Respond in JSON format:
{{
    "title": "...",
    "summary": "...",
    "content_markdown": "..."
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are the NUJ communications team writing guidance for members.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            import json
            result = json.loads(response.choices[0].message.content)
            logger.info("Guidance generated successfully")
            return result

        except Exception as e:
            logger.error(f"Guidance generation failed: {e}")
            return {
                "title": f"{platform_name} Policy Update",
                "summary": "Recent policy changes detected.",
                "content_markdown": "Please review the changes manually.",
            }


# Global analyzer instance
analyzer = PolicyAnalyzer()

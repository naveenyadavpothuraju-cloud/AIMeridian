"""Summariser service — generates 2–3 sentence summaries via claude-haiku-4-5."""

import logging
from typing import TYPE_CHECKING

import anthropic

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.models.content import Content

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 200
TEMPERATURE = 0

SYSTEM_PROMPT = """\
You are a technical content summariser for AIMeridian, a personal AI developments tracker.
Your job is to write a concise, informative 2–3 sentence summary of the content provided.

Rules:
- Focus on: what is new, why it matters, and who it affects
- Do NOT include generic phrases like "this paper presents" or "the authors propose"
- Do NOT repeat the title
- Use plain English; avoid jargon unless it is standard in AI/ML
- Write in present tense
- Maximum 3 sentences
- Return only the summary — no preamble, no labels, no markdown"""


class Summariser:
    """Summarises raw content items using Claude Haiku with hash-based caching via DB status."""

    def __init__(self, client: anthropic.Anthropic) -> None:
        self.client = client

    def summarise_item(
        self,
        title: str,
        raw_text: str,
        content_type: str,
        source_name: str,
        platform: str,
    ) -> str:
        """Call Claude Haiku to summarise a single item. Returns empty string on error."""
        user_prompt = (
            f"Title: {title}\n"
            f"Source: {platform} — {source_name}\n"
            f"Content type: {content_type}\n\n"
            f"{raw_text}"
        )
        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            block = response.content[0]
            text = block.text if hasattr(block, "text") else ""
            return text.strip()
        except anthropic.APIError as exc:
            logger.error("Summariser API error: %s", exc)
            return ""
        except Exception as exc:
            logger.error("Summariser unexpected error: %s", exc)
            return ""

    def run(self, db: "Session", items: "list[Content]") -> int:
        """Summarise all raw items in-place and commit. Returns count of items summarised."""
        count = 0
        for item in items:
            if item.status != "raw":
                continue
            if not item.raw_text:
                continue

            summary = self.summarise_item(
                title=item.title,
                raw_text=item.raw_text,
                content_type=item.content_type,
                source_name=item.source.name,
                platform=item.source.platform,
            )

            if summary:
                item.summary = summary
                item.status = "summarised"
                count += 1
            else:
                item.status = "failed"

        if items:
            db.commit()
        return count

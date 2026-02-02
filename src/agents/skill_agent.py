"""Agent-backed helper for skill fallback operations."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Tuple

from anthropic import Anthropic


class SkillAgent:
    """Lightweight agent wrapper for skill fallbacks."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = Anthropic()
        self.model = model
        self.logger = logging.getLogger(__name__)

    def extract_query_metadata(
        self, query_text: str, file_name: str, folder_name: str
    ) -> Dict[str, Any]:
        """Use the agent to extract metadata for a SQL query."""
        system_prompt = (
            "You are a SQL metadata extractor. Return only JSON with: "
            "query_type, table_name, complexity_score (0-1), "
            "has_teradata_functions (true/false), teradata_functions (list)."
        )

        user_prompt = f"""
Extract metadata for this SQL query.

File: {file_name}
Folder: {folder_name}

Query:
{query_text}
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text.strip()
        if "{" in content and "}" in content:
            json_str = content[content.find("{") : content.rfind("}") + 1]
            return json.loads(json_str)

        raise ValueError("Agent did not return valid JSON for metadata extraction")

    def validate_translation(self, original_query: str, translated_query: str) -> Tuple[bool, str]:
        """Agent-based validation of translation correctness."""
        system_prompt = (
            "You are a SQL validation agent. Respond with JSON: "
            "{\"valid\": true/false, \"reason\": \"short explanation\"}."
        )

        user_prompt = f"""
Validate whether the translated query preserves the logic of the original.

Original:
{original_query}

Translated:
{translated_query}
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text.strip()
        if "{" in content and "}" in content:
            json_str = content[content.find("{") : content.rfind("}") + 1]
            data = json.loads(json_str)
            return bool(data.get("valid", False)), str(data.get("reason", ""))

        return "valid" in content.lower(), content

    def summarize_report(self, validation_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Agent-based summarization when report generation fails."""
        system_prompt = (
            "You are a reporting agent. Summarize validation results and return JSON with: "
            "folders (dict), total_queries, total_passed, total_failed, pass_rate."
        )

        user_prompt = f"""
Summarize these validation results into a report JSON.

Payload:
{json.dumps(validation_payload, indent=2)}
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text.strip()
        if "{" in content and "}" in content:
            json_str = content[content.find("{") : content.rfind("}") + 1]
            return json.loads(json_str)

        raise ValueError("Agent did not return valid JSON for report summarization")
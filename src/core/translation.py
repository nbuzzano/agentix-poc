"""Translation engine for Teradata to Redshift queries"""

import os
import json
import logging
from typing import Optional, Tuple
from pathlib import Path
from anthropic import Anthropic
from .models import TranslationResult, TranslationStatus, QueryMetadata


class TranslationEngine:
    """
    Handles translation of Teradata queries to Redshift using Claude.
    Supports multiple strategies for better accuracy.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = Anthropic()
        self.model = model
        self.logger = logging.getLogger(__name__)

        # Load translation rules
        self.translation_rules = self._load_translation_rules()

    def translate(
        self,
        query_metadata: QueryMetadata,
        strategy: str = "basic",
        attempt_number: int = 1,
    ) -> TranslationResult:
        """
        Translate a single query using the specified strategy.
        
        Strategies:
        - basic: Simple direct translation
        - advanced: Analyzes structure and applies transformations
        - iterative: Breaks down complex queries into simpler parts
        """
        result = TranslationResult(
            query_metadata=query_metadata,
            attempt_number=attempt_number,
            strategy_used=strategy,
        )

        try:
            if strategy == "basic":
                translated = self._translate_basic(query_metadata.original_query)
            elif strategy == "advanced":
                translated = self._translate_advanced(query_metadata.original_query)
            elif strategy == "iterative":
                translated = self._translate_iterative(query_metadata.original_query)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            result.translated_query = translated
            result.status = TranslationStatus.SUCCESS

        except Exception as e:
            result.status = TranslationStatus.FAILED
            result.error_message = str(e)
            self.logger.error(
                f"Translation failed for {query_metadata.file_name}: {str(e)}"
            )

        return result

    def _translate_basic(self, query: str) -> str:
        """Basic translation using Claude with standard prompts"""
        system_prompt = """You are an expert SQL translator specializing in converting 
Teradata SQL to Amazon Redshift SQL. 
- Preserve query logic and functionality
- Use Redshift-compatible syntax
- Maintain table and column names
- Return only the translated query, no explanations"""

        user_prompt = f"""Translate this Teradata query to Redshift SQL:

{query}

Rules:
- Use Redshift data types and functions
- Replace Teradata-specific functions with Redshift equivalents
- Adjust date/time functions for Redshift
- Ensure the query is valid Redshift SQL"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return response.content[0].text.strip()

    def _translate_advanced(self, query: str) -> str:
        """Advanced translation with structural analysis"""
        system_prompt = """You are an expert SQL translator for Teradata to Redshift conversion.
Perform the following steps:
1. Analyze the query structure
2. Identify all Teradata-specific elements
3. Apply appropriate transformations
4. Ensure full compatibility with Redshift
Return only the translated query."""

        user_prompt = f"""Analyze and translate this Teradata query to Redshift:

{query}

Specifically:
- Check for QUALIFY clause (convert to WHERE with window functions)
- Check for SEL statement (convert to proper syntax)
- Ensure all date functions are Redshift compatible
- Verify aggregation functions compatibility
- Check for partition/distribution considerations"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return response.content[0].text.strip()

    def _translate_iterative(self, query: str) -> str:
        """Iterative translation breaking down complex queries"""
        # First pass: analyze
        system_prompt = """You are an expert SQL translator.
Break down this Teradata query into simpler components and translate each to Redshift.
Return the complete translated query."""

        user_prompt = f"""Break down and translate this Teradata query to Redshift:

{query}

Steps:
1. Identify main query components (FROM, WHERE, GROUP BY, etc.)
2. Identify any subqueries
3. Identify Teradata-specific functions
4. Translate each component
5. Reassemble into valid Redshift query"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return response.content[0].text.strip()

    def validate_translation(self, original_query: str, translated_query: str) -> Tuple[bool, str]:
        """
        Validate that translation preserves logic using Claude.
        Returns (is_valid, explanation)
        """
        system_prompt = """You are an expert SQL analyzer.
Validate that a Redshift translation preserves the logic of the original Teradata query.
Respond with JSON: {"valid": true/false, "reason": "explanation"}"""

        user_prompt = f"""Validate this translation:

Original Teradata:
{original_query}

Translated Redshift:
{translated_query}

Check if logic is preserved and syntax is valid."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        try:
            content = response.content[0].text.strip()
            # Try to parse as JSON
            if "{" in content and "}" in content:
                json_str = content[content.find("{") : content.rfind("}") + 1]
                data = json.loads(json_str)
                return data.get("valid", False), data.get("reason", "Unknown")
            else:
                return "valid" in content.lower(), content
        except Exception as e:
            self.logger.error(f"Error validating translation: {str(e)}")
            return False, str(e)

    def _load_translation_rules(self) -> dict:
        """Load static translation rules"""
        return {
            "teradata_functions": {
                "CURRENT_DATE": "CURRENT_DATE",
                "CURRENT_TIMESTAMP": "CURRENT_TIMESTAMP",
                "TRIM": "TRIM",
                "SUBSTRING": "SUBSTRING",
                "CAST": "CAST",
                "QUALIFY": None,  # Needs special handling
            },
            "data_types": {
                "BYTEINT": "SMALLINT",
                "INTEGER": "INTEGER",
                "BIGINT": "BIGINT",
                "DECIMAL": "DECIMAL",
                "REAL": "REAL",
                "VARCHAR": "VARCHAR",
                "CHAR": "CHAR",
                "DATE": "DATE",
                "TIMESTAMP": "TIMESTAMP",
            },
        }

    def batch_translate(
        self, queries: list[QueryMetadata], strategy: str = "basic"
    ) -> list[TranslationResult]:
        """Translate multiple queries"""
        results = []
        for i, query_meta in enumerate(queries, 1):
            self.logger.info(f"Translating query {i}/{len(queries)}: {query_meta.file_name}")
            result = self.translate(query_meta, strategy=strategy)
            results.append(result)
        return results

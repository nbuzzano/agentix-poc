---
name: translate-teradata-to-redshift
description: Translates Teradata SQL queries to Amazon Redshift-compatible SQL syntax, handling dialect differences, function mappings, and data type conversions.
---

# Translate Teradata to Redshift Skill

This skill takes Teradata SQL queries and translates them to Amazon Redshift-compatible syntax. It handles dialect-specific functions, data types, and optimizations specific to each database platform.

## Task

You are provided with Teradata SQL queries that need to be translated for execution on Amazon Redshift. Your task is to:

1. **Analyze the query**: Identify Teradata-specific syntax and functions that need translation
2. **Apply translation rules**:
   - Convert Teradata functions to Redshift equivalents (e.g., CAST with timezone handling)
   - Translate data types appropriately (TIMESTAMP WITH TIME ZONE → TIMESTAMP, etc.)
   - Replace Teradata-specific clauses (QUALIFY → HAVING alternatives, etc.)
   - Handle Teradata temporal tables and convert to Redshift-compatible patterns
   - Adjust indexing hints and optimization directives
3. **Preserve logic**: Ensure the translated query maintains the original business logic
4. **Optimize for Redshift**: Apply Redshift best practices where applicable
5. **Validate syntax**: Ensure the output is syntactically valid Redshift SQL

## Translation Mapping Examples

- QUALIFY clause → WHERE with window function result
- TIMESTAMP WITH TIME ZONE → TIMESTAMP (Redshift uses UTC)
- ROW_NUMBER() OVER (PARTITION BY x) → Keep as-is (Redshift supports it)
- Teradata CAST variants → Standard CAST with Redshift data types
- ANSI Temporal tables → Convert to standard query patterns
- FASTLOAD directives → Remove (not applicable to Redshift)

## Output Format

Provide the output as a JSON structure with this schema:
```json
{
  "folder_name": [
    {
      "file_name": "string",
      "original_query": "original Teradata query",
      "translated_query": "translated Redshift query",
      "translation_status": "SUCCESS|PARTIAL|FAILED",
      "issues": ["issue1", "issue2"],
      "notes": "explanation of changes made"
    }
  ]
}
```

## Examples

### Example 1: Simple QUALIFY Translation
- Input: `SELECT id, name, ROW_NUMBER() OVER (ORDER BY id) as rn FROM users QUALIFY ROW_NUMBER() OVER (ORDER BY id) = 1`
- Output: `SELECT id, name FROM (SELECT id, name, ROW_NUMBER() OVER (ORDER BY id) as rn FROM users) WHERE rn = 1`
- Status: SUCCESS

### Example 2: TIMESTAMP WITH TIME ZONE
- Input: `SELECT created_ts TIMESTAMP WITH TIME ZONE FROM events`
- Output: `SELECT created_ts FROM events`
- Status: SUCCESS with note about timezone conversion

## Guidelines

- Handle multi-line queries gracefully
- Preserve query formatting where possible
- If a translation is uncertain, mark as PARTIAL and explain in notes
- Include warnings about features that may affect performance
- Handle nested subqueries properly
- Maintain accurate line mapping between original and translated queries
- If translation completely fails, explain what feature is blocking translation

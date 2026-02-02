---
name: validate-queries
description: Validates translated SQL queries for syntax correctness and Redshift compatibility, identifying any remaining issues before execution.
---

# Validate Queries Skill

This skill validates that the translated Redshift queries are syntactically correct and compatible with Redshift's requirements. It identifies any remaining issues or warnings.

## Task

You are provided with translated Redshift SQL queries. Your task is to:

1. **Syntax validation**:
   - Check for SQL syntax errors according to Redshift grammar
   - Validate keywords, operators, and clause ordering
   - Ensure parentheses and quotes are properly balanced
   - Verify function signatures match Redshift's supported functions

2. **Redshift compatibility check**:
   - Verify data types are valid in Redshift
   - Check for unsupported functions or features
   - Validate schema references (public schema if not specified)
   - Identify potential performance issues or anti-patterns
   - Check for Teradata-isms that may have been missed

3. **Semantic validation**:
   - Ensure table and column references are reasonable
   - Check join conditions for logical correctness
   - Verify aggregate functions are used appropriately
   - Validate window function partitioning

4. **Generate detailed report**: For each query, provide:
   - Overall validation status
   - List of all errors found
   - List of warnings or best-practice suggestions
   - Recommendations for fixes

## Output Format

Provide the output as a JSON structure with this schema:
```json
{
  "folder_name": [
    {
      "file_name": "string",
      "validation_status": "VALID|INVALID|WARNING",
      "syntax_errors": ["error1", "error2"],
      "compatibility_issues": ["issue1", "issue2"],
      "warnings": ["warning1", "warning2"],
      "recommendations": ["recommendation1", "recommendation2"],
      "can_execute": true|false
    }
  ]
}
```

## Validation Rules

- **VALID**: No errors, no warnings
- **WARNING**: No errors but has non-critical issues or best-practice violations
- **INVALID**: Has one or more syntax or compatibility errors

## Examples

### Example 1: Valid Query
- Input: `SELECT id, name FROM users WHERE age > 18 ORDER BY name`
- Output: validation_status "VALID", can_execute true

### Example 2: Missing Schema
- Input: `SELECT * FROM table_name`
- Output: validation_status "WARNING", recommendations: ["Consider explicitly specifying schema (public.table_name)"]

### Example 3: Invalid Function
- Input: `SELECT TERADATA_PROPRIETARY_FUNC(col) FROM users`
- Output: validation_status "INVALID", syntax_errors: ["TERADATA_PROPRIETARY_FUNC is not a valid Redshift function"]

## Guidelines

- Be thorough but practical - focus on issues that would prevent execution
- Distinguish between blocking errors and improvements
- For warnings, provide actionable recommendations
- Consider both current Redshift version limitations and best practices
- Include helpful hints about how to fix issues
- Handle complex nested queries and CTEs properly
- Be lenient with naming conventions but strict about syntax

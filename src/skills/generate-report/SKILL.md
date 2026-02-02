---
name: generate-report
description: Generates comprehensive reports and logs documenting the query translation process, including statistics, validation results, and recommendations.
---

# Generate Report Skill

This skill synthesizes the results from the entire translation pipeline and generates comprehensive reports documenting the translation process, outcomes, and recommendations.

## Task

You are provided with the complete results from the read, translate, and validate skills. Your task is to:

1. **Aggregate statistics**:
   - Total number of queries processed
   - Breakdown by status (successful, failed, warnings)
   - Query type distribution (SELECT, INSERT, UPDATE, DELETE)
   - Average translation difficulty
   - Complexity distribution

2. **Generate summary report**:
   - Overall translation success rate
   - Key findings and insights
   - Major blockers or patterns in failed translations
   - Recommendations for pre-migration improvements

3. **Create detailed logs**:
   - Per-folder summary with query counts and status breakdown
   - Per-query translation details with before/after comparison
   - Issues identified and recommended fixes
   - Links to specific query files for review

4. **Identify patterns**:
   - Common Teradata constructs that caused issues
   - Queries that may need manual review
   - Performance optimization opportunities
   - Data type conversion patterns

5. **Generate output files**:
   - Executive summary (text format)
   - Detailed JSON report with full results
   - CSV summary for spreadsheet review
   - HTML report with visual breakdown (if applicable)

## Output Format

Provide the output as a JSON structure with this schema:
```json
{
  "summary": {
    "total_queries": number,
    "successful": number,
    "failed": number,
    "warnings": number,
    "success_rate": percentage,
    "processed_folders": number
  },
  "by_folder": {
    "folder_name": {
      "total": number,
      "successful": number,
      "failed": number,
      "warnings": number,
      "queries": [
        {
          "file_name": "string",
          "status": "SUCCESS|FAILED|WARNING",
          "issues_count": number,
          "translation_status": "string"
        }
      ]
    }
  },
  "statistics": {
    "by_type": { "SELECT": number, "INSERT": number, "UPDATE": number, "DELETE": number },
    "complexity_distribution": { "simple": number, "medium": number, "complex": number }
  },
  "recommendations": [
    "recommendation1",
    "recommendation2"
  ],
  "blockers": [
    "blocker1",
    "blocker2"
  ]
}
```

## Examples

### Example Summary
- 150 total queries processed
- 120 successful (80%)
- 20 with warnings (13%)
- 10 failed (7%)
- Key recommendation: "Consider manual review of 10 queries with Teradata temporal table syntax"

## Guidelines

- Focus on actionable insights
- Highlight patterns that might indicate systematic issues
- Provide context for failed translations
- Suggest remediation strategies
- Include performance considerations discovered during validation
- Make the report useful for both technical teams and stakeholders
- Organize information hierarchically (summary → folder → query level)
- Include timestamps for audit purposes

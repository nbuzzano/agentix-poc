---
name: read-queries
description: Reads and catalogs Teradata SQL queries from a specified input directory, extracting metadata about each query including type, complexity, and Teradata-specific functions used.
---

# Read Queries Skill

This skill is responsible for discovering and reading Teradata SQL query files from the input directory. It catalogs each query with metadata that will be used by downstream skills.

## Task

You are provided with access to a directory path containing SQL files. Your task is to:

1. **Explore the directory structure**: Scan the input folder and all subfolders to find SQL files (typically .sql or .txt extensions)
2. **Read and catalog queries**: For each SQL file found:
   - Extract the query content
   - Determine the query type (SELECT, INSERT, UPDATE, DELETE, etc.)
   - Identify Teradata-specific functions, syntax, or features used
   - Calculate a complexity score (simple/medium/complex based on query structure)
   - Extract table names being queried
3. **Organize by folder**: Group the queries by their containing folder/subfolder
4. **Generate metadata**: Create a structured output that includes:
   - File path and name
   - Query type
   - Table names
   - Teradata functions detected
   - Complexity assessment
   - Query preview (first 200 characters)

## Output Format

Provide the output as a JSON structure with this schema:
```json
{
  "folder_name": [
    {
      "file_name": "string",
      "query_type": "SELECT|INSERT|UPDATE|DELETE|other",
      "tables": ["table1", "table2"],
      "teradata_functions": ["function1", "function2"],
      "complexity_score": "simple|medium|complex",
      "query_preview": "first 200 chars of query"
    }
  ]
}
```

## Examples

### Example 1: Simple SELECT
- Input: A file `orders.sql` containing a basic SELECT from a single table
- Output: Query cataloged as type "SELECT", complexity "simple", with table "orders"

### Example 2: Complex Multi-table Query
- Input: A file with a query using INNER JOIN, window functions, and Teradata-specific QUALIFY clause
- Output: Query cataloged as type "SELECT", complexity "complex", teradata_functions: ["QUALIFY"]

## Guidelines

- Handle files with various encodings gracefully
- Skip non-SQL files or files that don't contain valid SQL queries
- Preserve the original query content exactly as found
- If a query spans multiple lines, read it completely
- Be thorough in detecting Teradata-specific syntax (QUALIFY, ANSI TEMPORAL tables, FastLoad, etc.)
- Group results by the immediate parent folder of each SQL file

# Agentix Skills Architecture

## Overview

Agentix now uses an **Agent-Based Skills** architecture where each step in the translation pipeline is implemented as a **Skill** - a declarative component defined by a `SKILL.md` file that Claude interprets and executes.

## What is a Skill?

A **Skill** is a folder containing:
- **SKILL.md**: A markdown file with:
  - YAML frontmatter (name, description)
  - Detailed instructions for Claude to follow
  - Examples and guidelines for the task
  - Expected output format (usually JSON)

The key insight: **Skills are agent-driven**, not code-driven. Claude reads the skill instructions and executes them intelligently.

## Available Skills

### 1. `read-queries`
**Purpose**: Discover and catalog Teradata SQL queries from the input directory

**Location**: `src/skills/read-queries/SKILL.md`

**What it does**:
- Scans the input folder for SQL files
- Extracts query metadata (type, complexity, functions used)
- Returns structured JSON with query catalog

**Example output**:
```json
{
  "folder_name": [
    {
      "file_name": "orders.sql",
      "query_type": "SELECT",
      "tables": ["orders"],
      "teradata_functions": [],
      "complexity_score": "simple",
      "query_preview": "SELECT * FROM orders WHERE date > ..."
    }
  ]
}
```

### 2. `translate-teradata-to-redshift`
**Purpose**: Translate Teradata SQL to Redshift-compatible syntax

**Location**: `src/skills/translate-teradata-to-redshift/SKILL.md`

**What it does**:
- Analyzes Teradata-specific syntax
- Applies translation rules (QUALIFY → WHERE alternatives, etc.)
- Converts data types appropriately
- Returns translated queries with status and notes

**Example output**:
```json
{
  "folder_name": [
    {
      "file_name": "orders.sql",
      "original_query": "...",
      "translated_query": "...",
      "translation_status": "SUCCESS",
      "issues": [],
      "notes": "No Teradata-specific syntax found"
    }
  ]
}
```

### 3. `validate-queries`
**Purpose**: Validate translated queries for Redshift compatibility

**Location**: `src/skills/validate-queries/SKILL.md`

**What it does**:
- Checks SQL syntax validity
- Validates Redshift compatibility
- Identifies unsupported functions
- Returns validation results with warnings

**Example output**:
```json
{
  "folder_name": [
    {
      "file_name": "orders.sql",
      "validation_status": "VALID",
      "syntax_errors": [],
      "compatibility_issues": [],
      "warnings": [],
      "recommendations": [],
      "can_execute": true
    }
  ]
}
```

### 4. `generate-report`
**Purpose**: Aggregate results and generate comprehensive reports

**Location**: `src/skills/generate-report/SKILL.md`

**What it does**:
- Aggregates statistics from all previous skills
- Identifies patterns and blockers
- Generates recommendations
- Returns summary report and detailed findings

**Example output**:
```json
{
  "summary": {
    "total_queries": 150,
    "successful": 120,
    "failed": 10,
    "warnings": 20,
    "success_rate": 0.80
  },
  "statistics": {
    "by_type": { "SELECT": 100, "INSERT": 30 },
    "complexity_distribution": { "simple": 80, "medium": 50, "complex": 20 }
  },
  "recommendations": [
    "Review 10 queries with Teradata temporal table syntax",
    "Consider performance optimization for 5 complex queries"
  ]
}
```

## Pipeline Execution Flow

```
Input (Teradata SQL queries)
        ↓
   [read-queries skill]
        ↓
   Query metadata + catalog
        ↓
   [translate-teradata-to-redshift skill]
        ↓
   Translated queries + issues
        ↓
   [validate-queries skill]
        ↓
   Validation results + warnings
        ↓
   [generate-report skill]
        ↓
Output (Reports, logs, validated Redshift queries)
```

## How SkillManager Works

The `SkillManager` class (`src/agents/skill_manager.py`):

1. **Loads a skill**: Reads the SKILL.md file and parses YAML frontmatter
2. **Builds prompt**: Constructs a detailed prompt for Claude including:
   - Skill name and description
   - Full instructions from SKILL.md
   - Input data (context, previous results)
   - Expected output format
3. **Calls Claude**: Sends the prompt to Claude 3.5 Sonnet
4. **Parses result**: Extracts JSON response from Claude's reply

```python
# Example usage
skill_manager = SkillManager(config)
result = skill_manager.execute_skill(
    "read-queries",
    input_data={
        "input_path": "/data/input",
        "file_extensions": [".sql", ".txt"]
    },
    context="Read and catalog all Teradata queries"
)
```

## TranslationOrchestrator

The `TranslationOrchestrator` class coordinates the entire pipeline:

```python
orchestrator = TranslationOrchestrator(config)
result = orchestrator.execute_full_pipeline(max_retries=3)

# Returns:
# {
#   "status": "success",
#   "read_results": {...},
#   "translate_results": {...},
#   "validate_results": {...},
#   "report": {...},
#   "logs_path": "..."
# }
```

## CLI Usage

```bash
# Run full pipeline
agentix translate \
  --input ./data/input \
  --output ./data/output \
  --logs ./logs \
  --strategy advanced \
  --log-level DEBUG

# Run a single skill
agentix skill read-queries \
  --input ./data/input \
  --output ./data/output
```

## Why This Architecture?

1. **Agent-Driven**: Skills are interpreted by Claude, enabling intelligent, context-aware execution
2. **Declarative**: Define tasks as instructions, not code
3. **Flexible**: Easy to modify instructions without changing code
4. **Maintainable**: Skills are self-documenting via SKILL.md files
5. **Extensible**: Add new skills by creating new SKILL.md files
6. **Composable**: Skills can be chained with outputs from previous skills

## Creating a New Skill

1. Create a new folder: `src/skills/my-skill-name/`
2. Create `SKILL.md` with YAML frontmatter and instructions:
   ```markdown
   ---
   name: my-skill-name
   description: What this skill does
   ---
   
   # My Skill Name
   
   [Instructions for Claude...]
   
   ## Output Format
   [JSON schema...]
   ```
3. Call from orchestrator:
   ```python
   result = skill_manager.execute_skill("my-skill-name", input_data=data)
   ```

## Key Differences from Previous Architecture

| Aspect | Previous | Current |
|--------|----------|---------|
| **Implementation** | Python classes (Step subclasses) | Declarative SKILL.md files |
| **Execution** | Python code execution | Claude interprets instructions |
| **Flexibility** | Code-based, requires changes | Instruction-based, easy to modify |
| **Logic** | Deterministic Python + agent fallback | Pure agent interpretation |
| **Skill Inputs** | Object instances | Structured JSON data |
| **Skill Outputs** | Python objects/dicts | Parsed JSON |
| **Extensibility** | Add new Step classes | Add new SKILL.md folders |

## Error Handling

If a skill fails:
1. SkillManager catches exceptions during Claude API calls
2. Returns error response: `{"status": "ERROR", "error": "...", "skill": "..."}`
3. Orchestrator detects error and stops pipeline
4. Error is logged and reported to user

## Monitoring and Debugging

Enable detailed logging to see skill execution:

```bash
agentix translate --log-level DEBUG
```

This shows:
- Which skills are being executed
- Full prompts sent to Claude (in DEBUG mode)
- Claude's responses and parsing
- Execution time for each skill
- Any errors or warnings

## Future Enhancements

- Skill caching to avoid re-processing
- Parallel skill execution for independent tasks
- Skill versioning and rollback
- Custom skill parameters
- Skill composition and chaining helpers

# Agentix Agent-Based Skills Architecture - Quick Start

## What Changed?

Agentix has been completely refactored from a **code-based step architecture** to an **Agent-Based Skills architecture**. Instead of Python classes that execute logic, skills are now **declarative instructions that Claude interprets**.

### Key Differences

| Before | After |
|--------|-------|
| Python classes extending `Step` | Folders with `SKILL.md` files |
| Code-based execution logic | Claude interprets instructions |
| Limited flexibility | Easy to modify instructions |
| Hard to understand for non-devs | Self-documenting instructions |

## The New Architecture

```
src/skills/
├── read-queries/
│   └── SKILL.md              # Instructions for reading SQL files
├── translate-teradata-to-redshift/
│   └── SKILL.md              # Instructions for translating queries
├── validate-queries/
│   └── SKILL.md              # Instructions for validation
└── generate-report/
    └── SKILL.md              # Instructions for report generation
```

Each `SKILL.md` contains:
- **YAML frontmatter** (name, description)
- **Detailed instructions** for Claude to follow
- **Examples** of expected behavior
- **Output format** (usually JSON)

## How It Works

1. **SkillManager** reads the SKILL.md file
2. Builds a detailed prompt for Claude with:
   - Skill instructions
   - Input data (context from previous skills)
   - Expected output format
3. **Claude** interprets the instructions and executes the task
4. Returns JSON result to the pipeline

## Running Agentix

### 1. Full Pipeline

```bash
# Run the complete translation pipeline
agentix translate \
  --input ./data/input \
  --output ./data/output \
  --logs ./logs \
  --log-level DEBUG

# Simplified
agentix translate
```

This executes all 4 skills in sequence:
1. **read-queries** - Catalog SQL files
2. **translate-teradata-to-redshift** - Translate to Redshift
3. **validate-queries** - Validate compatibility
4. **generate-report** - Create reports

### 2. Individual Skills

```bash
# List available skills
agentix skills list

# Run a single skill
agentix skills run read-queries \
  --input ./data/input \
  --output ./data/output

agentix skills run translate-teradata-to-redshift \
  --data-file ./logs/read_queries_output.json

agentix skills run validate-queries \
  --data-file ./logs/translate_teradata_to_redshift_output.json

agentix skills run generate-report \
  --data-file ./logs/validate_queries_output.json
```

## Project Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Initialize project structure
agentix init

# 4. Run the pipeline
agentix translate --log-level DEBUG
```

## Skill Details

### read-queries
- **Purpose**: Discover and catalog all Teradata SQL queries
- **Input**: Directory path with SQL files
- **Output**: JSON with query metadata (type, complexity, functions, tables)
- **Location**: `src/skills/read-queries/SKILL.md`

### translate-teradata-to-redshift
- **Purpose**: Translate Teradata SQL to Redshift-compatible syntax
- **Input**: Query catalog from read-queries
- **Output**: JSON with translated queries and translation status
- **Location**: `src/skills/translate-teradata-to-redshift/SKILL.md`

**Handles**:
- QUALIFY clauses → WHERE alternatives
- TIMESTAMP WITH TIME ZONE → TIMESTAMP
- Teradata functions → Redshift equivalents
- Data type conversions
- Temporal table patterns

### validate-queries
- **Purpose**: Validate translated queries for Redshift compatibility
- **Input**: Translated queries from translate skill
- **Output**: JSON with validation results and warnings
- **Location**: `src/skills/validate-queries/SKILL.md`

**Checks**:
- SQL syntax validity
- Redshift function support
- Data type compatibility
- Query performance patterns

### generate-report
- **Purpose**: Synthesize results and generate comprehensive reports
- **Input**: Results from all previous skills
- **Output**: JSON report with statistics, recommendations, blockers
- **Location**: `src/skills/generate-report/SKILL.md`

**Generates**:
- Overall statistics and success rates
- Per-folder summaries
- Issue patterns and blockers
- Recommendations for fixes

## Output Files

After running the pipeline, check:

```
logs/
├── read_queries_output.json              # Cataloged queries
├── translate_teradata_to_redshift_output.json  # Translated queries
├── validate_queries_output.json          # Validation results
└── generate_report_output.json           # Final report
```

## Example Output

When you run `agentix translate`, you'll see:

```
🚀 Starting Agentix Translation Pipeline (Agent-Based Skills)
   Input:  ./data/input
   Output: ./data/output
   Logs:   ./logs
   Strategy: basic
   Max Retries: 3

==================================================
[1/4] Executing read-queries skill...
[2/4] Executing translate-teradata-to-redshift skill...
[3/4] Executing validate-queries skill...
[4/4] Executing generate-report skill...

==================================================
✅ Pipeline Completed Successfully!

📖 Read Queries Skill:
   Status: SUCCESS
   Folders processed: 3
   Total queries: 45

🔄 Translate Skill:
   Status: SUCCESS

✔️  Validate Skill:
   Status: SUCCESS

📊 Generate Report Skill:
   Total Items: 45
   Successful: 40
   Failed: 3
   Warnings: 2

Logs: ./logs
==================================================
```

## Key Files

- **SkillManager**: `src/agents/skill_manager.py`
  - Loads SKILL.md files
  - Builds prompts for Claude
  - Executes skills and parses responses

- **TranslationOrchestrator**: `src/agents/orchestrator.py`
  - Coordinates skill execution pipeline
  - Handles error management
  - Chains results between skills

- **CLI**: `src/cli.py`
  - Updated with `skills` commands
  - `skills list` - List available skills
  - `skills run` - Execute individual skills

## Troubleshooting

### No ANTHROPIC_API_KEY

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-..."
# or edit .env file
```

### Skill fails with "No queries found"

Make sure:
1. Input directory exists: `./data/input/`
2. SQL files are present
3. Files have .sql or .txt extension

### Claude API errors

Check:
1. API key is valid and has quota
2. Network connection is active
3. Claude 3.5 Sonnet model is available

### Debugging

Enable debug logging:

```bash
agentix translate --log-level DEBUG
```

This shows:
- Full prompts sent to Claude
- Claude's responses
- Skill execution times
- Error details

## Next Steps

1. **Add your queries**: Put Teradata SQL files in `./data/input/`
2. **Run the pipeline**: `agentix translate`
3. **Review results**: Check output files in `./logs/`
4. **Customize skills**: Edit SKILL.md files to adjust behavior
5. **Create new skills**: Add new SKILL.md files for custom tasks

## Documentation

For more details, see:
- [SKILLS_ARCHITECTURE.md](../docs/SKILLS_ARCHITECTURE.md) - Detailed architecture
- [docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) - Contributing guide
- [docs/QUICK_START.md](../docs/QUICK_START.md) - Original quick start

## Support

For issues or questions:
1. Check logs: `tail -f logs/*.log`
2. Enable debug: `--log-level DEBUG`
3. Review skill instructions: `src/skills/*/SKILL.md`
4. Check CLI help: `agentix --help`

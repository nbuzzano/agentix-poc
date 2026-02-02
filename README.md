# Agentix PoC - Teradata to Redshift Query Translator

🚀 Agentic system for translating Teradata SQL queries to Amazon Redshift using Claude-powered Skills.

## 🎯 What is Agentix?

Agentix is an **Agent-Based Skills Architecture** for SQL query translation. Instead of traditional code-based steps, each phase of the translation pipeline is defined as a declarative **Skill** - a folder with a `SKILL.md` file that Claude interprets and executes intelligently.

### Key Features

- 🤖 **Agent-Powered**: Claude interprets skill instructions for flexible, intelligent execution
- 📁 **Declarative Skills**: Define tasks as markdown instructions, not code
- 🔄 **Multi-Phase Pipeline**: Read → Translate → Validate → Report
- 📊 **Comprehensive Validation**: Syntax checking and Redshift compatibility analysis
- 📝 **Detailed Logging**: Results saved as JSON for analysis
- 🛠️ **Extensible**: Add new skills by creating new SKILL.md files
- 💻 **Easy CLI**: Simple commands for full pipeline or individual skills

## Architecture Overview

```
SKILL = Folder with SKILL.md file
        ↓
        Instructions for Claude to follow
        ↓
        Claude executes and returns JSON
        ↓
        Next skill in pipeline
```

### 4 Core Skills

1. **read-queries** - Catalog SQL files with metadata
2. **translate-teradata-to-redshift** - Translate to Redshift syntax
3. **validate-queries** - Validate compatibility
4. **generate-report** - Create comprehensive reports

## 🚀 Quick Start (5 minutes)

```bash
# 1. Clone and enter
git clone <repo>
cd agentix-poc

# 2. Install
bash install.sh

# 3. Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY

# 4. Run
agentix translate --log-level DEBUG
```

**Output**: Check `./logs/` for results and reports

## 📦 Installation


```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup configuration
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

## 💻 CLI Commands

### Full Pipeline (Recommended)

```bash
# Basic (uses default paths)
agentix translate

# With custom options
agentix translate \
  --input ./my-queries/ \
  --output ./redshift-queries/ \
  --logs ./execution-logs/ \
  --strategy advanced \
  --log-level DEBUG
```

### Individual Skills

```bash
# List available skills
agentix skills list

# Run specific skill
agentix skills run read-queries
agentix skills run translate-teradata-to-redshift
agentix skills run validate-queries
agentix skills run generate-report
```

### Project Initialization

```bash
# Initialize project structure
agentix init

# Shows project info
agentix info
```

## 🎯 How It Works

### Pipeline Flow

```
1. read-queries          → Catalog SQL files with metadata
   ↓
2. translate-teradata-to-redshift → Translate to Redshift syntax
   ↓
3. validate-queries      → Validate compatibility and syntax
   ↓
4. generate-report       → Create comprehensive reports
```

### Each Skill

A **Skill** is a folder containing:
- **SKILL.md**: Instructions for Claude
- **YAML frontmatter**: name, description
- **Examples & Guidelines**: How to execute

Example (`src/skills/read-queries/SKILL.md`):
```markdown
---
name: read-queries
description: Reads and catalogs SQL queries from a directory
---

# Read Queries Skill

[Instructions for Claude to follow...]

## Output Format
[Expected JSON schema...]
```

## 📊 Results and Logging

Output files are saved as JSON:

```
logs/
├── read_queries_output.json              # Cataloged queries
├── translate_teradata_to_redshift_output.json  # Translated queries
├── validate_queries_output.json          # Validation results
└── generate_report_output.json           # Final report
```

**Información capturada**:
- Cada intento de traducción
- Resultados de validación
- Errores y advertencias
- Timestamps exactos

## 🧪 Desarrollo y Testing

```bash
# Ejecutar tests
pytest tests/ -v --cov=src/

# Lint y format
ruff check src/
black src/

# Type checking
mypy src/

# Instalar dev tools
pip🏗️ Arquitectura del Pipeline

### 4 Pasos Modulares

```
Input Queries (Teradata)
    ↓
[1️⃣  ReadQueriesStep]
  - Lee archivos .sql
  - Extrae metadata
  - Detecta Teradata-specifics
    ↓
[2️⃣  TranslateStep]
  - Llama Claude API
  - Reintenta con 3 estrategias
  - Valida lógica preservada
    ↓
[3️⃣  ValidateStep]
  - Valida sintaxis SQL
  - Detección Redshift-compatible
  - Análisis determinístico
    ↓
[4️⃣  ReportStep]
  - Agrupa resultados
  - Genera logs JSON
  - Crea resumen final
    ↓
Output Queries (Redshift) + Comprehensive Logs
```

## 📚 Documentación

- **QUICK_START.md** - Guía de 5 minutos
- **USAGE_ES.md** - Guía completa en español
- **ARCHITECTURE.md** - Detalles técnicos
- **CONTRIBUTING.md** - Cómo contribuir
- **PROJECT_SUMMARY.md** - Resumen del proyecto

## 🔌 Arquitectura Técnica

- **Modular**: 4 steps independientes
- **Determinístico**: Lógica en Python, IA en traducción
- **Observable**: Logging multinivel
- **Extensible**: Fácil agregar estrategias
- **Escalable**: Soporta 1000+ querie

# Type checking
mypy src/
```

## Arquitectura

### Paso 1: Lectura de Queries
- Lee todas las queries de carpetas
- Extrae metadatos (tabla, complejidad, etc.)

### Paso 2: Traducción
- Agente IA traduce Teradata → Redshift
- Reintenta con diferentes estrategias

### Paso 3: Validación
- Genera datos sintéticos
- Ejecuta ambas versiones
- Compara resultados

### Paso 4: Logging
- Registra estado por tabla
- Genera reportes por carpeta
- Resume ejecutables/fallidos

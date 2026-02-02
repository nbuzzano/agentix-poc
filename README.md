# Agentix PoC - Teradata to Redshift Query Translator

🚀 Sistema agentico modular y determinístico para traducir queries de Teradata a Redshift con validaciones automáticas y logging completo.

## Características Principales

- 🤖 **IA + Determinismo**: Claude para traducción + código Python para lógica
- 🔄 **Reintentos Inteligentes**: 3 estrategias (básica, avanzada, iterativa)
- 📊 **Validación Determinística**: Sin ejecución real, análisis sintáctico robusto
- 📝 **Logging Multinivel**: Por tabla, carpeta y resumen general
- 🛠️ **Arquitectura Modular**: 4 pasos independientes, fácil extensión
- 💻 **CLI Flexible**: Flujo completo o pasos individuales
- ✅ **Production-Ready**: Código profesional, bien documentado

## Estructura del Proyecto

```
agentix-poc/
├── src/
│   ├── core/               # Componentes centrales
│   ├── steps/              # Pasos ejecutables (determinísticos)
│   ├── agents/             # Orquestadores de agentes
│   ├── utils/              # Utilidades y helpers
│   └── main.py            # Punto de entrada
├── data/
│   ├── input/             # Queries de entrada (Teradata)
│   └── output/            # Queries traducidas (Redshift)
├── logs/                  # Logs de ejecución
└── tests/                 # Tests unitarios
```

## 🚀 Quick Start (2 minutos)

```bash
# 1. Entrar al directorio
cd /home/nbuzzano/repositories/agentix-poc

# 2. Instalar (automático)
bash install.sh

# 3. Configurar
cp .env.example .env
# Editar .env: ANTHROPIC_API_KEY=sk-ant-xxxxx

# 4. Ejecutar
source venv/bin/activate
agentix translate
```

## 📦 Instalación Detallada

```bash
# Entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Dependencias
pip install -e ".[dev]"

# Configuración
cp .env.example .env
# Editar .env con tu ANTHROPIC_API_KEY
```

## 💻 Uso de la CLI

### Flujo Completo (Recomendado)

```bash
# Básico (usa valores por defecto)
agentix translate

# Con opciones personalizadas
agentix translate \
  --input ./data/input \
  --output ./data/output \
  --logs ./logs \
  --strategy advanced \
  --max-retries 5 \
  --log-level DEBUG
```

### Pasos Individuales

```bash
# Ver pasos disponibles
agentix steps list

# Ejecutar cada paso
agentix steps run read_queries
agentix steps run translate --max-retries 3
age🔧 Estrategias de Traducción

| Estrategia | Descripción | Mejor para |
|-----------|------------|-----------|
| **basic** | Traducción simple y directa | Queries simples, punto de partida |
| **advanced** | Análisis estructural + transformaciones | Queries con Teradata-específicos |
| **iterative** | Desglosa en partes, traduce, reasambla | Queries muy complejas |

Ejemplo:
```bash
agentix translate --strategy advanced --max-retries 5
```

## 📊 Logging y Reportes

El sistema genera logs en múltiples niveles:

```
logs/
├── agentix.log                 # Log real-time
├── summary.json                # Resumen general
├── tables/
│   ├── customer_orders.json    # Detalles por tabla
│   └── ...
└── folders/
    ├── root.json               # Resumen por carpeta
    └── ...
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

# Arquitectura de Agentix

## Descripción General

Agentix es un sistema modular para traducir queries de Teradata a Redshift usando Claude como motor de IA. La arquitectura sigue principios SOLID y está diseñada para ser:

- **Modular**: Cada paso es independiente
- **Determinística**: Código Python determina el comportamiento
- **Extensible**: Fácil agregar nuevas estrategias
- **Observable**: Logging detallado en múltiples niveles

## Componentes Principales

```
agentix-poc/
├── src/
│   ├── core/                      # Componentes centrales
│   │   ├── models.py              # Data models (QueryMetadata, TranslationResult, etc.)
│   │   ├── file_handler.py        # I/O determinístico
│   │   ├── logger.py              # Sistema de logging
│   │   └── translation.py         # Motor de traducción con Claude
│   │
│   ├── steps/                     # Pipeline steps (determinísticos)
│   │   ├── read_queries_step.py   # Lee queries de carpetas
│   │   ├── translate_step.py      # Traduce con reintentos
│   │   ├── validate_step.py       # Valida con datos sintéticos
│   │   └── report_step.py         # Genera reportes
│   │
│   ├── agents/                    # Orquestadores
│   │   └── orchestrator.py        # Coordina todo el pipeline
│   │
│   ├── utils/                     # Utilidades
│   │   ├── config.py              # Configuración
│   │   └── sql_validator.py       # Validador SQL
│   │
│   └── cli.py                     # CLI
│
├── data/
│   ├── input/                     # Queries Teradata de entrada
│   ├── output/                    # Queries Redshift traducidas
│   └── synthetic/                 # Datos sintéticos para validación
│
├── logs/
│   ├── agentix.log                # Log general
│   ├── summary.json               # Resumen de ejecución
│   ├── tables/                    # Logs por tabla
│   │   ├── customer_orders.json
│   │   └── ...
│   └── folders/                   # Logs por carpeta
│       ├── sales.json
│       └── ...
│
└── tests/                         # Tests unitarios
```

## Flujo de Datos

```
Input Queries (Teradata SQL)
    ↓
[ReadQueriesStep]
    ↓
QueryMetadata[] (estructurado)
    ↓
[TranslateStep] → Claude API
    ↓
TranslationResult[] (con reintentos)
    ↓
[ValidateStep] → SQL Validator
    ↓
ValidationResult[] (sintaxis + compatibilidad)
    ↓
[ReportStep]
    ↓
Output Queries (Redshift SQL) + Logs detallados
```

## Data Models

### QueryMetadata
```python
{
    file_name: "query1.sql",
    file_path: "/path/to/query1.sql",
    folder_name: "sales",
    table_name: "customer_orders",
    query_type: "SELECT",
    original_query: "SELECT ...",
    complexity_score: 0.6,
    has_teradata_functions: true,
    teradata_functions: ["QUALIFY", "TRIM"]
}
```

### TranslationResult
```python
{
    query_metadata: QueryMetadata,
    translated_query: "SELECT ...",
    status: "SUCCESS",
    attempt_number: 2,
    strategy_used: "advanced",
    error_message: null,
    execution_time_ms: 2450.5
}
```

### ValidationResult
```python
{
    translation_result: TranslationResult,
    status: "PASSED",
    passed: true,
    execution_details: "Tables: [...], Columns: [...]",
    synthetic_data_generated: false,
    rows_compared: 0
}
```

## Pipeline Steps

### 1. ReadQueriesStep
**Objetivo**: Leer y parsear todas las queries de las carpetas de entrada.

**Determinístico**: Sí
- Lee archivos .sql en orden consistente
- Extrae metadata de forma determinística
- No depende de APIs externas

**Salida**: `Dict[folder_name, List[QueryMetadata]]`

### 2. TranslateStep
**Objetivo**: Traducir queries usando Claude con lógica de reintentos.

**Determinístico**: Parcialmente
- La lógica de reintentos es determinística (mismas entradas → mismo comportamiento)
- Las respuestas de Claude varían, pero los reintentos siguen un patrón

**Estrategias**:
1. **basic**: Traducción simple
2. **advanced**: Análisis estructural
3. **iterative**: Desglosa en partes

**Salida**: `Dict[folder_name, List[TranslationResult]]`

### 3. ValidateStep
**Objetivo**: Validar las queries traducidas.

**Determinístico**: Sí
- Análisis sintáctico determinístico
- Detección de patrones compatible con Redshift
- No ejecuta queries contra DB

**Validaciones**:
1. Sintaxis SQL válida
2. Compatibilidad Redshift
3. Extracción de tablas/columnas

**Salida**: `Dict[folder_name, List[ValidationResult]]`

### 4. ReportStep
**Objetivo**: Generar reportes y logs.

**Determinístico**: Sí
- Agrupa resultados de forma determinística
- Escribe a disco en carpetas estructuradas

**Salida**:
- `logs/tables/*.json` - Detalles por tabla
- `logs/folders/*.json` - Resumen por carpeta
- `logs/summary.json` - Resumen general

## Sistema de Logging

### Arquitectura Multinivel

```
┌─────────────────────────────────────────┐
│         Logging System                   │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Real-time Log (agentix.log)      │   │
│  │ - Eventos en tiempo real          │   │
│  │ - Nivel configurable              │   │
│  │ - A consola y archivo             │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ Structured Logs (JSON)           │   │
│  │ - Por tabla                       │   │
│  │ - Por carpeta                     │   │
│  │ - Resumen general                 │   │
│  └──────────────────────────────────┘   │
│                                          │
└─────────────────────────────────────────┘
```

### Información Capturada

**Por Tabla**:
- Todos los intentos de traducción
- Resultados de validación
- Errores y advertencias
- Timestamps

**Por Carpeta**:
- Cantidad total de queries
- Traducidas exitosamente
- Validadas
- Pasadas

**Resumen General**:
- Estadísticas por paso
- Tasa de éxito general
- Configuración utilizada
- Información de ejecución

## Extensibilidad

### Agregar Nueva Estrategia

1. Editar `TranslationEngine._translate_nueva_estrategia()`:
```python
def _translate_nueva_estrategia(self, query: str) -> str:
    """Nueva estrategia"""
    # Lógica personalizada
    return translated_query
```

2. Actualizar `translate()` para usar la estrategia:
```python
if strategy == "nueva":
    translated = self._translate_nueva_estrategia(query)
```

### Agregar Nuevo Paso

1. Crear `src/steps/nuevo_step.py`:
```python
class NuevoStep:
    def __init__(self, config: Config, logger: AgentixLogger):
        ...
    
    def execute(self, input_data) -> tuple[output_data, StepResult]:
        ...
```

2. Registrar en `TranslationOrchestrator.execute_step()`:
```python
elif step_name == "nuevo":
    step = NuevoStep(...)
    result = step.execute(...)
```

### Agregar Validador Personalizado

1. Crear en `src/utils/sql_validator.py`:
```python
def custom_validation(self, query: str) -> Tuple[bool, str]:
    """Validación personalizada"""
    ...
```

2. Usar en `ValidateStep._validate_translation()`:
```python
custom_valid, custom_msg = self.sql_validator.custom_validation(...)
```

## CLI Architecture

```
agentix
├── translate                  # Flujo completo
│   ├── --input
│   ├── --output
│   ├── --strategy
│   ├── --max-retries
│   └── --log-level
│
├── steps
│   ├── list                   # Ver pasos disponibles
│   └── run                    # Ejecutar paso específico
│       ├── --data-file
│       └── [step_name]
│
├── init                       # Inicializar proyecto
│
└── info                       # Información de configuración
    └── --format
```

## Configuración

Todas las configuraciones en `Config` (src/utils/config.py):

- **Paths**: INPUT, OUTPUT, LOGS, SYNTHETIC_DATA
- **API**: ANTHROPIC_API_KEY, MODEL
- **Pipeline**: LOG_LEVEL, MAX_RETRIES, TRANSLATION_STRATEGY
- **Validación**: VALIDATE_SYNTAX, VALIDATE_WITH_DATA, SYNTHETIC_DATA_ROWS

Puede ser sobrescrita por:
1. Variables de entorno (.env)
2. Argumentos CLI
3. Directamente en código

## Performance

### Optimizaciones

1. **File I/O**: Lee archivos una sola vez, cachea en memoria
2. **Logging**: Logs asincronos, no bloquean pipeline
3. **API Calls**: Batch translation cuando es posible
4. **Validation**: Análisis sintáctico sin ejecución real

### Escalabilidad

- Soporta 1000+ queries
- Logging eficiente con archivos JSON
- Memoria constante por query

## Testing

### Estrategia de Test

- Unit tests por componente
- Integration tests por step
- E2E tests para pipeline completo

```bash
# Ejecutar tests
pytest tests/ -v --cov=src/

# Tests específicos
pytest tests/test_translation.py -v
pytest tests/test_validation.py -v
```

## Seguridad

- API key almacenada en .env (nunca en código)
- No ejecuta queries contra BD real
- Validación de entrada
- Error handling robusto

## Futuras Mejoras

1. **Caché de traducciones**: Evitar traducir queries idénticas
2. **Ejecución paralela**: Traducir múltiples queries simultáneamente
3. **Feedback loop**: Aprender de traducciones exitosas
4. **ML basado en patrones**: Detectar patrones Teradata comunes
5. **Integración con BD**: Ejecutar queries contra BD de prueba

# Agentix PoC - Teradata to Redshift Query Translator

Sistema agentico para traducir queries de Teradata a Redshift con validaciones automáticas usando datos sintéticos.

## Características

- 🤖 **Agentes Inteligentes**: Usa Claude para traducción y validación
- 🔄 **Reintentos Automáticos**: Múltiples estrategias con reintento configurable
- 📊 **Validación Determinística**: Código Python determinístico para máxima confiabilidad
- 📝 **Logging Detallado**: Logs por tabla, carpeta y resumen general
- 🛠️ **Modular**: Arquitectura paso a paso fácil de extender
- 💻 **CLI Flexible**: Ejecuta el flujo completo o pasos específicos

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

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -e ".[dev]"

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu ANTHROPIC_API_KEY
```

## Uso

### CLI - Flujo Completo

```bash
agentix translate --input data/input --output data/output --max-retries 3
```

### CLI - Paso Específico

```bash
# Ver disponibles
agentix steps list

# Ejecutar paso específico
agentix steps run read_queries --input data/input
agentix steps run translate --input data/input --output temp
agentix steps run validate --queries temp --synthetic-data data/synthetic
agentix steps run generate_reports --logs logs
```

### Configuración

- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR
- `MAX_RETRIES`: Número de reintentos por tabla fallida
- `TRANSLATION_STRATEGY`: basic, advanced, iterative

## Estrategias de Reintento

1. **Basic**: Ajusta instrucciones de traducción
2. **Advanced**: Analiza errores y propone correcciones
3. **Iterative**: Desglosa la query en partes menores

## Logging

Los logs se generan en múltiples niveles:

- `logs/tables/[table_name].json`: Detalle por tabla
- `logs/folders/[folder_name].json`: Resumen por carpeta
- `logs/summary.json`: Resumen general

## Desarrollo

```bash
# Tests
pytest tests/ -v --cov

# Lint
ruff check src/
black src/

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

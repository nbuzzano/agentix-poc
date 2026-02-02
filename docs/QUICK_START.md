# Guía Rápida - Agentix

## Instalación (2 minutos)

```bash
# 1. Entrar al directorio
cd /home/nbuzzano/repositories/agentix-poc

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar
pip install -e ".[dev]"

# 4. Configurar API key
cp .env.example .env
# Editar .env y agregar: ANTHROPIC_API_KEY=sk-ant-...
```

## Uso Básico

```bash
# Ejecutar pipeline completo
agentix translate

# Ver pasos disponibles
agentix steps list

# Ejecutar paso específico
agentix steps run read_queries
agentix steps run translate
agentix steps run validate
agentix steps run report

# Ver configuración
agentix info
```

## Estructura de Archivos

```
agentix-poc/
├── src/
│   ├── core/               # Modelos, archivos, logger, traducción
│   ├── steps/              # Pasos determinísticos (read, translate, validate, report)
│   ├── agents/             # Orquestador del pipeline
│   ├── utils/              # Config, validador SQL
│   └── cli.py              # Interfaz de línea de comandos
├── data/
│   ├── input/              # ← Aquí van tus queries Teradata
│   └── output/             # ← Aquí van las queries Redshift traducidas
├── logs/                   # ← Logs detallados de ejecución
├── tests/                  # Tests unitarios
├── README.md               # Descripción del proyecto
├── ARCHITECTURE.md         # Detalles de arquitectura
├── USAGE_ES.md             # Guía completa en español
└── QUICK_START.md          # ← Este archivo
```

## Flujo de Trabajo Típico

### 1. Agregar Queries
```bash
# Copiar tus queries Teradata a data/input/
cp /ruta/a/tus/queries/*.sql ./data/input/

# O crear subcarpetas
mkdir ./data/input/sales
cp /ruta/a/sales/*.sql ./data/input/sales/
```

### 2. Ejecutar Traducción
```bash
# Opción 1: Automático (recomendado para empezar)
agentix translate

# Opción 2: Con opciones personalizadas
agentix translate --strategy advanced --max-retries 5
```

### 3. Revisar Resultados
```bash
# Ver resumen general
cat ./logs/summary.json

# Ver detalles por carpeta
cat ./logs/folders/sales.json

# Ver detalles por tabla
cat ./logs/tables/customer_orders.json

# Ver queries traducidas
ls -la ./data/output/
cat ./data/output/sales/query1.translated.sql
```

## Estrategias de Traducción

| Estrategia | Descripción | Cuando usar |
|-----------|-------------|-------------|
| **basic** | Traducción directa simple | Queries simples, punto de partida |
| **advanced** | Análisis estructural + transformaciones | Queries con Teradata-específicos |
| **iterative** | Desglosa en partes, traduce, reasambla | Queries muy complejas |

## Ejemplos

```bash
# Ejemplo 1: Traducir con estrategia basic (predeterminado)
agentix translate

# Ejemplo 2: Usar estrategia advanced
agentix translate --strategy advanced

# Ejemplo 3: Aumentar reintentos para queries problemáticas
agentix translate --strategy iterative --max-retries 5

# Ejemplo 4: Ver logs en tiempo real
tail -f ./logs/agentix.log

# Ejemplo 5: Debug mode
agentix translate --log-level DEBUG
```

## Interpretar Logs

### Logs en tiempo real (agentix.log)
```
2024-02-02 14:25:30,123 - agentix - INFO - Starting ReadQueriesStep
2024-02-02 14:25:31,456 - agentix - INFO - Found 6 queries in 1 folders
2024-02-02 14:25:35,789 - agentix - INFO - Translating 6 queries in folder 'root'
2024-02-02 14:25:45,012 - agentix - INFO - ✓ 01_simple_select.sql translated successfully
...
```

### Resumen (summary.json)
```json
{
  "timestamp": "2024-02-02T14:26:00.123456",
  "total_tables": 6,
  "step_results": [
    {
      "step_name": "read_queries",
      "status": "SUCCESS",
      "total_items": 6,
      "successful_items": 6,
      "success_rate": 100.0
    },
    {
      "step_name": "translate",
      "status": "SUCCESS",
      "total_items": 6,
      "successful_items": 5,
      "success_rate": 83.3
    }
  ]
}
```

## Troubleshooting

| Problema | Solución |
|---------|----------|
| "ANTHROPIC_API_KEY not set" | Ejecutar: `echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env` |
| "No queries found" | Verificar: `ls -la ./data/input/` |
| Queries vacías traducidas | Aumentar retries: `--max-retries 5` |
| Error de sintaxis | Ver logs: `agentix translate --log-level DEBUG` |

## Variables de Entorno Importantes

```bash
# API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Paths (opcional)
DATA_INPUT_PATH=./data/input
DATA_OUTPUT_PATH=./data/output
LOGS_PATH=./logs

# Pipeline (opcional)
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
MAX_RETRIES=3                 # Número de reintentos
TRANSLATION_STRATEGY=basic    # basic, advanced, iterative
```

## Desarrollo

```bash
# Ejecutar tests
pytest tests/ -v

# Linting
ruff check src/

# Type checking
mypy src/

# Formateo automático
black src/
```

## Próximos Pasos

1. **Primeros Pasos**:
   - Instalar dependencias ✓
   - Configurar API key
   - Ejecutar `agentix init`
   - Ejecutar primer `agentix translate`

2. **Uso Avanzado**:
   - Explorar estrategias diferentes
   - Revisar logs en detalle
   - Customizar reintentos

3. **Desarrollo**:
   - Agregar validadores personalizados
   - Implementar nuevas estrategias
   - Extender steps del pipeline

## Documentación Completa

- `README.md` - Descripción general del proyecto
- `ARCHITECTURE.md` - Detalles técnicos de la arquitectura
- `USAGE_ES.md` - Guía completa con ejemplos extensos
- `QUICK_START.md` - Esta guía rápida

## Preguntas Frecuentes

**¿Cuánto tiempo toma traducir N queries?**
- Aproximadamente 1-2 segundos por query (sin reintentos)
- Depende de la complejidad y API latency

**¿Puedo interrumpir la traducción?**
- Sí, presionar Ctrl+C
- Los logs se preservan

**¿Qué pasa si una query falla?**
- Se registra en logs y se continúa con la siguiente
- Se reintenta N veces con estrategias diferentes

**¿Cómo rechazo queries traducidas incorrectamente?**
- Revisar en `./data/output/`
- Editar manualmente si es necesario
- Los logs mantienen historial

---

**¿Necesitas ayuda?** Revisa los logs o la documentación completa en ARCHITECTURE.md

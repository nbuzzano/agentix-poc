# Ejemplos de uso del proyecto Agentix

## 1. Instalación Inicial

```bash
# Clonar el repositorio
cd /home/nbuzzano/repositories/agentix-poc

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -e ".[dev]"

# Copiar configuración
cp .env.example .env

# Editar .env y agregar tu API key
# ANTHROPIC_API_KEY=sk-ant-...
```

## 2. Inicializar Proyecto

```bash
# Crear estructura de carpetas y ejemplo
agentix init
```

Esto crea:
- `./data/input/` - Carpeta para queries Teradata
- `./data/output/` - Carpeta para queries traducidas
- `./data/synthetic/` - Datos sintéticos para validación
- `./logs/` - Logs de ejecución
- Un archivo de ejemplo: `./data/input/example_query.sql`

## 3. Agregar tus Queries

Coloca tus queries de Teradata en `./data/input/`:

```bash
# Ejemplo: copiar queries
cp my_queries/*.sql ./data/input/

# Puedes organizar en subcarpetas
mkdir ./data/input/sales
cp sales_queries/*.sql ./data/input/sales/

mkdir ./data/input/customer
cp customer_queries/*.sql ./data/input/customer/
```

## 4. Ejecutar Pipeline Completo

```bash
# Modo básico (traducción simple)
agentix translate --strategy basic

# Modo avanzado (análisis estructural)
agentix translate --strategy advanced

# Modo iterativo (desglosa queries complejas)
agentix translate --strategy iterative

# Personalizado
agentix translate \
  --input ./data/input \
  --output ./data/output \
  --logs ./logs \
  --strategy advanced \
  --max-retries 5 \
  --log-level DEBUG
```

## 5. Ejecutar Pasos Individuales

### Ver pasos disponibles
```bash
agentix steps list
```

### Ejecutar paso: Leer queries
```bash
agentix steps run read_queries \
  --input ./data/input \
  --logs ./logs
```

### Ejecutar paso: Traducir
```bash
agentix steps run translate \
  --input ./data/input \
  --output ./data/output \
  --logs ./logs \
  --max-retries 3
```

### Ejecutar paso: Validar
```bash
agentix steps run validate \
  --input ./data/input \
  --output ./data/output \
  --logs ./logs
```

### Ejecutar paso: Generar reportes
```bash
agentix steps run report \
  --logs ./logs
```

## 6. Ver Información

```bash
# Mostrar configuración actual (texto)
agentix info

# Mostrar configuración actual (JSON)
agentix info --format json
```

## 7. Entender los Logs

```bash
# Logs generales
cat ./logs/agentix.log

# Resumen de ejecución
cat ./logs/summary.json

# Logs por carpeta
cat ./logs/folders/sales.json
cat ./logs/folders/customer.json

# Logs detallados por tabla
cat ./logs/tables/customer_orders.json
cat ./logs/tables/product_sales.json
```

## 8. Estructura de Salida

Después de ejecutar `agentix translate`:

```
./data/output/
├── sales/
│   ├── sales_query_1.translated.sql
│   ├── sales_query_2.translated.sql
│   └── ...
├── customer/
│   ├── customer_query_1.translated.sql
│   └── ...
└── root/
    └── example_query.translated.sql

./logs/
├── agentix.log
├── summary.json
├── tables/
│   ├── customer_orders.json
│   ├── product_sales.json
│   └── ...
└── folders/
    ├── sales.json
    ├── customer.json
    └── root.json
```

## 9. Interpretar Resultados

### Summary.json - Resumen General
```json
{
  "timestamp": "2024-02-02T...",
  "total_tables": 5,
  "step_results": [
    {
      "step_name": "read_queries",
      "status": "SUCCESS",
      "total_items": 8,
      "successful_items": 8,
      "success_rate": 100.0
    },
    ...
  ]
}
```

### Folder Summary - Resumen por Carpeta
```json
{
  "folder_name": "sales",
  "total_queries": 3,
  "translated": 3,
  "validated": 3,
  "passed": 2,
  "queries": [...]
}
```

### Table Logs - Detalles por Tabla
```json
{
  "table_name": "customer_orders",
  "total_entries": 2,
  "logs": [
    {
      "timestamp": "2024-02-02T...",
      "folder": "sales",
      "type": "translation",
      "result": {...}
    },
    {
      "timestamp": "2024-02-02T...",
      "folder": "sales",
      "type": "validation",
      "result": {...}
    }
  ]
}
```

## 10. Estrategias de Traducción

### basic
- Traducción simple y directa
- Uso de prompts estándar
- Más rápida pero menos precisa
- Buen punto de partida

### advanced
- Análisis de estructura de query
- Identifica elementos Teradata-específicos
- Aplica transformaciones contextuales
- Recomendada para queries complejas

### iterative
- Desglosa queries en componentes
- Traduce cada componente
- Reasambla el resultado
- Mejor para queries muy complejas

## 11. Variables de Entorno

```bash
# En .env
ANTHROPIC_API_KEY=sk-ant-...
DATA_INPUT_PATH=./data/input
DATA_OUTPUT_PATH=./data/output
LOGS_PATH=./logs
LOG_LEVEL=INFO
MAX_RETRIES=3
TRANSLATION_STRATEGY=basic
VALIDATE_SYNTAX=true
VALIDATE_WITH_DATA=true
SYNTHETIC_DATA_ROWS=100
```

## 12. Desarrollo y Testing

```bash
# Ejecutar tests
pytest tests/ -v

# Coverage
pytest tests/ --cov=src

# Linting
ruff check src/

# Formateo
black src/

# Type checking
mypy src/
```

## 13. Troubleshooting

### Error: ANTHROPIC_API_KEY not set
```bash
# Solución: agregar API key a .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### Error: No queries found
```bash
# Verificar que las queries están en ./data/input
ls -la ./data/input/

# El archivo debe tener extensión .sql
# Ejemplo correcto: query1.sql
```

### Queries traducidas están vacías
```bash
# Aumentar max retries
agentix translate --max-retries 5

# Cambiar estrategia
agentix translate --strategy advanced

# Ver logs detallados
agentix translate --log-level DEBUG
tail -f ./logs/agentix.log
```

### Validación falla para todas las queries
```bash
# Verificar que las queries originales son válidas
# Aumentar timeout o cambiar validador
```

# 🚀 COMIENZA AQUÍ - Agentix

## ¿Qué se creó?

Un **sistema agentico profesional y modular** para traducir queries de Teradata a Redshift con:
- ✅ Traducción con Claude (3 estrategias)
- ✅ Reintentos automáticos
- ✅ Validación determinística
- ✅ Logging completo (tabla, carpeta, resumen)
- ✅ CLI flexible
- ✅ Código modular y extensible

## ⚡ Quick Start (3 minutos)

### 1. Instalar

```bash
cd /home/nbuzzano/repositories/agentix-poc
bash install.sh
```

### 2. Configurar API Key

```bash
# Editar .env
nano .env

# Buscar la línea y reemplazar:
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 3. Ejecutar

```bash
# Activar venv (si no está activado)
source venv/bin/activate

# Ejecutar pipeline
agentix translate
```

### 4. Ver Resultados

```bash
# Queries traducidas
ls -la ./data/output/

# Ver logs
cat ./logs/summary.json

# Ver detalles por tabla
cat ./logs/tables/*.json
```

## 📂 Estructura del Proyecto

```
/home/nbuzzano/repositories/agentix-poc/
│
├── 📦 src/
│   ├── core/           ← Modelos, I/O, logger, traducción
│   ├── steps/          ← Pipeline: read, translate, validate, report
│   ├── agents/         ← Orquestador
│   ├── utils/          ← Config y validador SQL
│   └── cli.py          ← Interfaz línea de comandos
│
├── 📂 data/
│   ├── input/          ← Queries Teradata (6 ejemplos incluidos)
│   ├── output/         ← Queries Redshift traducidas
│   └── synthetic/      ← Datos para validación
│
├── 📝 logs/            ← Logging detallado
│   ├── agentix.log     ← Log real-time
│   ├── summary.json    ← Resumen final
│   ├── tables/         ← Por tabla
│   └── folders/        ← Por carpeta
│
├── 🧪 tests/           ← Tests unitarios listos
│
└── 📚 Documentación
    ├── README.md           ← Descripción
    ├── QUICK_START.md      ← Esta guía rápida
    ├── USAGE_ES.md         ← Guía completa (español)
    ├── ARCHITECTURE.md     ← Detalles técnicos
    ├── PROJECT_SUMMARY.md  ← Resumen completo
    └── CONTRIBUTING.md     ← Para desarrolladores
```

## 🎯 Casos de Uso

### Caso 1: Traducir Queries Existentes

```bash
# 1. Copiar tus queries
cp /ruta/a/tus/queries/*.sql ./data/input/

# 2. Ejecutar traducción
agentix translate

# 3. Revisar resultados
ls -la ./data/output/
cat ./logs/summary.json
```

### Caso 2: Explorar Diferentes Estrategias

```bash
# Básico (rápido)
agentix translate --strategy basic

# Avanzado (más preciso)
agentix translate --strategy advanced

# Iterativo (para queries complejas)
agentix translate --strategy iterative --max-retries 5
```

### Caso 3: Ejecución Paso a Paso

```bash
# Ver pasos disponibles
agentix steps list

# Ejecutar cada paso manualmente
agentix steps run read_queries
agentix steps run translate
agentix steps run validate
agentix steps run report
```

## 📊 Entender los Logs

### 1. Summary.json (Resumen General)

```bash
cat ./logs/summary.json
```

Muestra:
- Queries totales
- Traducidas exitosamente
- Validadas
- Tasa de éxito general

### 2. Por Carpeta

```bash
cat ./logs/folders/root.json
```

Muestra detalles por cada carpeta de queries.

### 3. Por Tabla

```bash
cat ./logs/tables/customer_orders.json
```

Muestra:
- Todos los intentos de traducción
- Validación
- Errores si los hay

### 4. Real-time

```bash
tail -f ./logs/agentix.log
```

Ve eventos en tiempo real.

## 🔧 Configuración Común

### Aumentar Reintentos

```bash
agentix translate --max-retries 5
```

### Debug Mode

```bash
agentix translate --log-level DEBUG
tail -f ./logs/agentix.log
```

### Cambiar Rutas

```bash
agentix translate \
  --input ./mi_input \
  --output ./mi_output \
  --logs ./mi_logs
```

## 📦 Ejemplos Incluidos

El proyecto incluye 6 queries de ejemplo:

1. **01_simple_select.sql** - Query simple
2. **02_qualify_example.sql** - Con QUALIFY (Teradata-specific)
3. **03_complex_joins.sql** - Con JOINs
4. **04_cte_example.sql** - Con CTE
5. **05_window_functions.sql** - Window functions
6. **06_union_example.sql** - Con UNION

## 🧪 Probar sin Datos Reales

```bash
# El proyecto incluye ejemplos
# Simplemente ejecuta:
agentix translate

# Los 6 ejemplos serán traducidos
# Revisa los resultados en ./data/output/
```

## 🔌 Integración con tus Queries

```bash
# 1. Crear subcarpeta para tus queries
mkdir ./data/input/mi_proyecto

# 2. Copiar tus queries
cp /ruta/a/mis_queries/*.sql ./data/input/mi_proyecto/

# 3. Ejecutar
agentix translate

# 4. Revisar
ls -la ./data/output/mi_proyecto/
cat ./logs/folders/mi_proyecto.json
```

## ⚠️ Troubleshooting

| Problema | Solución |
|---------|----------|
| Error: ANTHROPIC_API_KEY | Editar .env con tu API key |
| No encuentra queries | Asegurar que están en ./data/input/ |
| Queries traducidas vacías | Aumentar reintentos: --max-retries 5 |
| No ve cambios | Revisar ./data/output/ (no input) |

## 📚 Documentación Completa

- **QUICK_START.md** - Guía visual de 5 minutos
- **USAGE_ES.md** - Guía exhaustiva con 50+ ejemplos
- **ARCHITECTURE.md** - Para desarrolladores
- **PROJECT_SUMMARY.md** - Visión general completa

## 🚀 Próximos Pasos

1. **Ahora** (1 min):
   ```bash
   bash install.sh
   nano .env  # Agregar API key
   ```

2. **Inmediato** (2 min):
   ```bash
   source venv/bin/activate
   agentix translate
   ```

3. **Verificar** (1 min):
   ```bash
   cat ./logs/summary.json
   ls -la ./data/output/
   ```

4. **Tus Queries** (5 min):
   ```bash
   cp /ruta/a/tus/queries/*.sql ./data/input/
   agentix translate
   ```

## 🆘 ¿Problemas?

1. Ver logs en tiempo real:
   ```bash
   tail -f ./logs/agentix.log
   ```

2. Ejecutar en debug mode:
   ```bash
   agentix translate --log-level DEBUG
   ```

3. Revisar documentación:
   - QUICK_START.md (5 min)
   - USAGE_ES.md (completa)
   - ARCHITECTURE.md (técnica)

## ✨ Características Destacadas

✅ **Determinístico**: Código Python controla flujo, no solo IA
✅ **Modular**: 4 pasos independientes, extensible
✅ **Observable**: Logging en 3 niveles
✅ **Robusto**: Reintentos con 3 estrategias
✅ **Profesional**: Code ready for production

## 📞 Resumen

**Tienes un sistema completo y listo para usar** que puede:
- Traducir cualquier cantidad de queries Teradata
- Validarlas automáticamente
- Registrar todo en logs detallados
- Reintentar con diferentes estrategias si falla
- Ejecutarse desde CLI con muchas opciones

**Estado**: 🟢 Listo para usar

---

## 🎓 Para Aprender Más

1. Lee QUICK_START.md (5 minutos)
2. Lee USAGE_ES.md si necesitas características avanzadas
3. Lee ARCHITECTURE.md si vas a contribuir
4. Revisa PROJECT_SUMMARY.md para visión completa

¡**Ahora a traducir! 🚀**

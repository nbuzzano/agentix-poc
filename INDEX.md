# Agentix - Índice de Documentación

## 🚀 Punto de Inicio

**→ Comienza aquí:** [START_HERE.md](docs/START_HERE.md) (3 minutos)

## 📖 Documentación Disponible

### Para Usuarios

| Documento | Tiempo | Contenido |
|-----------|--------|-----------|
| [START_HERE.md](docs/START_HERE.md) | 3 min | Inicio inmediato + casos de uso |
| [QUICK_START.md](docs/QUICK_START.md) | 5 min | Guía visual paso a paso |
| [USAGE_ES.md](docs/USAGE_ES.md) | 30 min | Guía completa con 50+ ejemplos |
| [README.md](docs/README.md) | 10 min | Descripción general del proyecto |

### Para Desarrolladores

| Documento | Tiempo | Contenido |
|-----------|--------|-----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 20 min | Arquitectura técnica detallada |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | 10 min | Guía para contribuyentes |
| [PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | 10 min | Visión técnica y características |

### Reportes

| Documento | Contenido |
|-----------|----------|
| [COMPLETION_REPORT.md](docs/COMPLETION_REPORT.md) | Resumen de lo que se entregó |

## 🎯 Rutas de Aprendizaje

### 🟢 Quiero empezar AHORA (5 minutos)
1. Lee [START_HERE.md](docs/START_HERE.md)
2. Ejecuta `bash install.sh`
3. Ejecuta `agentix translate`

### 🟡 Quiero entender cómo funciona (15 minutos)
1. Lee [QUICK_START.md](docs/QUICK_START.md)
2. Lee [README.md](docs/README.md)
3. Prueba ejemplos en [USAGE_ES.md](docs/USAGE_ES.md)

### 🔵 Quiero aprender la arquitectura (45 minutos)
1. Lee [PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
2. Lee [ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. Explora el código en `src/`

### 🟣 Quiero contribuir (60 minutos)
1. Lee [CONTRIBUTING.md](docs/CONTRIBUTING.md)
2. Lee [ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. Revisa `tests/` para entender testing

## 📂 Estructura de Carpetas

```
agentix-poc/
├── 📖 Documentación           ← Léeme primero
│   ├── START_HERE.md          ← COMIENZA AQUÍ
│   ├── QUICK_START.md
│   ├── USAGE_ES.md
│   ├── ARCHITECTURE.md
│   ├── README.md
│   ├── CONTRIBUTING.md
│   └── PROJECT_SUMMARY.md
│
├── 💻 Código
│   ├── src/
│   │   ├── core/              (Modelos, I/O, logger, traducción)
│   │   ├── steps/             (Pipeline: read, translate, validate, report)
│   │   ├── agents/            (Orquestrador)
│   │   ├── utils/             (Config, validador SQL)
│   │   └── cli.py             (CLI)
│   └── tests/                 (Tests unitarios)
│
├── 📊 Datos
│   ├── input/                 (Queries Teradata de entrada)
│   ├── output/                (Queries Redshift traducidas)
│   ├── synthetic/             (Datos sintéticos)
│   └── logs/                  (Logs de ejecución)
│
└── 🛠️ Configuración
    ├── pyproject.toml         (Dependencias)
    ├── .env.example           (Variables de entorno)
    ├── install.sh             (Script de instalación)
    └── main.py                (Punto de entrada)
```

## ⚡ Comandos Rápidos

```bash
# Instalar
bash install.sh

# Configurar
nano .env

# Ejecutar
source venv/bin/activate
agentix translate

# Ver ayuda
agentix --help
agentix steps list

# Desarrollo
pytest tests/ -v --cov=src/
ruff check src/
black src/
```

## 🎓 Conceptos Clave

### Flujo Principal
```
Queries Teradata → ReadQueriesStep → TranslateStep → ValidateStep → ReportStep → Queries Redshift + Logs
```

### 3 Estrategias de Traducción
- **basic**: Traducción simple
- **advanced**: Análisis estructural
- **iterative**: Desglosa en partes

### Logging Multinivel
- `agentix.log` - Real-time
- `summary.json` - Resumen general
- `tables/*.json` - Por tabla
- `folders/*.json` - Por carpeta

### Reintentos Automáticos
- Hasta 3 intentos por query
- Diferentes estrategias
- Fallback automático

## 📞 Respuestas Rápidas

**P: ¿Por dónde empiezo?**
R: Lee [START_HERE.md](docs/START_HERE.md) en 3 minutos

**P: ¿Cómo instalo?**
R: Ejecuta `bash install.sh` y listo

**P: ¿Cómo uso mis queries?**
R: Cópialas a `./data/input/` y ejecuta `agentix translate`

**P: ¿Dónde ven los resultados?**
R: En `./data/output/` y `./logs/`

**P: ¿Cómo veo los logs?**
R: `cat ./logs/summary.json` o `tail -f ./logs/agentix.log`

**P: ¿Qué estrategia usar?**
R: `--strategy basic` para empezar, luego prueba `advanced`

**P: ¿Cómo contribuyo?**
R: Lee [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 🔗 Enlaces Útiles

- 🏠 [README](docs/README.md) - Descripción general
- 🚀 [START_HERE](docs/START_HERE.md) - Inicio inmediato
- ⚡ [QUICK_START](docs/QUICK_START.md) - Guía visual
- 📖 [USAGE_ES](docs/USAGE_ES.md) - Guía completa
- 🏗️ [ARCHITECTURE](docs/ARCHITECTURE.md) - Detalles técnicos
- 🤝 [CONTRIBUTING](docs/CONTRIBUTING.md) - Cómo contribuir
- ✅ [COMPLETION_REPORT](docs/COMPLETION_REPORT.md) - Resumen del proyecto

---

**Estado**: ✅ Proyecto completo y listo para usar

**Recomendación**: Comienza por [START_HERE.md](docs/START_HERE.md)

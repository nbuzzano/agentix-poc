# Contributing to Agentix

¡Bienvenido! Las contribuciones son muy importantes para mejorar Agentix.

## Guía de Contribución

### Reportar Bugs

Si encuentras un bug:

1. Verifica que no esté reportado en Issues
2. Abre un nuevo Issue con:
   - Título descriptivo
   - Descripción detallada
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Logs relevantes

### Proponer Mejoras

1. Abre una Discussion o Issue
2. Describe la mejora con detalle
3. Explica por qué sería útil

### Hacer Cambios de Código

1. **Fork** el repositorio
2. **Branch** para tu feature: `git checkout -b feature/my-feature`
3. **Commit** tus cambios: `git commit -m 'Add my feature'`
4. **Test** tu código: `pytest tests/ -v`
5. **Push**: `git push origin feature/my-feature`
6. **Pull Request** con descripción detallada

### Estándares de Código

- **Python**: PEP 8, Black formatter
- **Type hints**: Usa anotaciones de tipo
- **Docstrings**: Toda función debe tener docstring
- **Tests**: Escribe tests para nuevo código

```bash
# Verificar código
ruff check src/
black src/
mypy src/

# Ejecutar tests
pytest tests/ -v --cov=src/
```

### Arquitectura Modular

Cuando agregas nuevas funcionalidades:

1. **Crea Step**: Si es un paso nuevo del pipeline
2. **Crea Componente Core**: Si es lógica fundamental
3. **Actualiza CLI**: Si es accesible por CLI
4. **Agrega Tests**: Tests unitarios + integration

Ejemplo para nuevo Step:

```python
# src/steps/my_new_step.py
class MyNewStep:
    def __init__(self, config: Config, logger: AgentixLogger):
        self.config = config
        self.logger = logger
    
    def execute(self, input_data) -> tuple[output_data, StepResult]:
        """Ejecuta el step y retorna resultado"""
        start_time = time.time()
        # Tu lógica aquí
        result = StepResult(...)
        self.logger.log_step(result)
        return output_data, result
```

### Commits

Usa mensajes descriptivos:

```
✨ Add new translation strategy (iterative)
🐛 Fix validation error handling
📝 Update documentation
🔧 Configure logging
🧪 Add tests for new feature
```

Prefijos:
- ✨ Feature
- 🐛 Bug
- 📝 Documentation
- 🔧 Configuration
- 🧪 Tests
- ♻️  Refactoring
- 🚀 Performance

## Estructura de PRs

1. **Descripción clara** de cambios
2. **Link a Issue** relacionado
3. **Checklist de testing**:
   - [ ] Código sigue PEP 8
   - [ ] Tests pasando
   - [ ] Documentación actualizada
   - [ ] Logs funcionando

## Desarrollo Local

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Desarrollo
# Edita código, tests, documentación

# Validación
pytest tests/ -v
ruff check src/
black src/
mypy src/

# Commit y push
git add .
git commit -m "✨ Your feature"
git push origin feature/your-feature
```

## Roadmap

### Corto Plazo
- [ ] Integración con BD de prueba
- [ ] Ejecución paralela de traducciones
- [ ] Caché de traducciones

### Mediano Plazo
- [ ] UI Web para pipeline
- [ ] Soporte para múltiples BD
- [ ] Machine learning para detección de patrones

### Largo Plazo
- [ ] Integración CI/CD automática
- [ ] Marketplace de strategies
- [ ] Cloud deployment

## Contacto

- 📧 Email: maintainer@agentix.dev (cambiar)
- 💬 Discussions: GitHub Discussions
- 📌 Issues: GitHub Issues

---

¡Gracias por contribuir a Agentix! 🙌

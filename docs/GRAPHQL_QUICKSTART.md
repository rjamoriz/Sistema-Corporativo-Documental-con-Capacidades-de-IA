# 🚀 GraphQL Server - Quick Start

## ✅ Servidor Funcionando

El servidor GraphQL está corriendo en:

```
🎮 GraphQL Playground: http://localhost:8000/api/graphql/
🏥 Health Check:       http://localhost:8000/api/graphql/health
📊 Main Health:        http://localhost:8000/health
```

---

## 🎯 Cómo Iniciarlo

### Opción 1: Servidor de Prueba (Recomendado para desarrollo)

```bash
cd backend
python test_graphql_server.py
```

Este servidor incluye:
- ✅ GraphQL API completo
- ✅ CORS habilitado
- ✅ Hot reload
- ✅ Sin dependencias de base de datos

### Opción 2: Servidor Completo (Producción)

```bash
cd backend
python main.py
```

Requiere:
- PostgreSQL corriendo
- Variables de entorno configuradas
- Todas las dependencias instaladas

---

## 🎮 Usar GraphQL Playground

1. **Abrir en navegador:**
   ```
   http://localhost:8000/api/graphql/
   ```

2. **Ejemplo de Query:**
   ```graphql
   query {
     documents(limit: 5) {
       id
       filename
       status
     }
   }
   ```

3. **Ejemplo de Mutation:**
   ```graphql
   mutation {
     uploadDocument(file: $file) {
       success
       message
     }
   }
   ```

---

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
pip install strawberry-graphql[fastapi] fastapi uvicorn pydantic-settings
```

### Error: "Port 8000 already in use"
```bash
# Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9

# O usar otro puerto
uvicorn test_graphql_server:app --port 8001
```

### Error: "Schema not found"
Asegúrate de estar en el directorio `backend/`:
```bash
cd backend
python test_graphql_server.py
```

---

## 📝 Notas

- El servidor de prueba usa **mocks** para los servicios
- Para testing completo, usa `python main.py` con DB
- GraphQL Playground incluye autocompletado (Ctrl+Space)
- Docs interactivos en el panel derecho del Playground

---

**Status:** ✅ FUNCIONANDO  
**Last Updated:** 10 de octubre de 2025

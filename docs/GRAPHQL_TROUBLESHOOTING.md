# 🔧 GraphQL Server Troubleshooting

## ✅ Estado Actual: FUNCIONANDO

El servidor GraphQL está **completamente operativo** en:
```
http://localhost:8000/api/graphql/
```

## 🧪 Verificaciones Rápidas

### 1. Verificar que el servidor está corriendo
```bash
ps aux | grep test_graphql_server
```
**Esperado:** Ver un proceso de Python corriendo `test_graphql_server.py`

### 2. Verificar respuesta HTTP
```bash
curl -v http://localhost:8000/api/graphql/
```
**Esperado:** 
- Status: `HTTP/1.1 200 OK`
- Content-Type: `text/html; charset=utf-8`
- Body: HTML con `<title>Strawberry GraphiQL</title>`

### 3. Probar consulta GraphQL
```bash
curl -X POST http://localhost:8000/api/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```
**Esperado:** `{"data": {"__typename": "Query"}}`

### 4. Verificar schema types
```bash
curl -X POST http://localhost:8000/api/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```
**Esperado:** JSON con lista de tipos: Document, Entity, Chunk, Annotation, etc.

### 5. Health check
```bash
curl http://localhost:8000/health
```
**Esperado:** `{"status": "healthy", "service": "GraphQL Test"}`

## 🐛 Solución de Problemas

### Problema: "Connection refused"

**Síntoma:**
```bash
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Solución:**
```bash
# Detener cualquier proceso anterior
pkill -f test_graphql_server

# Iniciar servidor
cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend
nohup python test_graphql_server.py > /tmp/graphql_server.log 2>&1 &

# Esperar 2 segundos
sleep 2

# Verificar
curl http://localhost:8000/health
```

### Problema: "El navegador no carga GraphiQL"

**Posibles causas:**
1. **Caché del navegador** - Hacer hard refresh: `Ctrl+F5` o `Cmd+Shift+R`
2. **Popup blocker** - Verificar que no esté bloqueado
3. **URL incorrecta** - Usar exactamente: `http://localhost:8000/api/graphql/` (con trailing slash)

**Solución:**
1. Cerrar todas las pestañas del navegador
2. Limpiar caché del navegador
3. Abrir nueva pestaña privada/incógnito
4. Navegar a: `http://localhost:8000/api/graphql/`

### Problema: "Error 500 Internal Server Error"

**Solución:**
```bash
# Ver logs del servidor
tail -50 /tmp/graphql_server.log

# Buscar errores de Python
grep -i "error\|traceback" /tmp/graphql_server.log
```

### Problema: "Cannot query field 'X' on type 'Y'"

**Causa:** Campo GraphQL no existe en el schema

**Solución:**
Ver campos disponibles en GraphiQL Playground o ejecutar:
```bash
curl -X POST http://localhost:8000/api/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __type(name: \"Document\") { fields { name type { name } } } }"}'
```

## 📊 Consultas de Prueba

### Introspección básica
```graphql
{
  __schema {
    queryType {
      name
      fields {
        name
        description
      }
    }
  }
}
```

### Listar tipos
```graphql
{
  __schema {
    types {
      name
      kind
    }
  }
}
```

### Ver campos de Document
```graphql
{
  __type(name: "Document") {
    name
    fields {
      name
      type {
        name
        kind
      }
    }
  }
}
```

### Consulta de documentos (mock data)
```graphql
{
  documents(limit: 5) {
    id
    filename
    status
    size
    mimeType
    uploadedAt
  }
}
```

## 🔍 Logs en Tiempo Real

### Ver logs del servidor
```bash
tail -f /tmp/graphql_server.log
```

### Filtrar solo errores
```bash
tail -f /tmp/graphql_server.log | grep -i error
```

### Ver últimas 100 líneas
```bash
tail -100 /tmp/graphql_server.log
```

## 🚀 Reinicio Completo

Si nada funciona, reinicio completo:
```bash
# 1. Detener servidor
pkill -f test_graphql_server

# 2. Limpiar logs
> /tmp/graphql_server.log

# 3. Verificar puerto libre
lsof -i :8000

# 4. Si hay algo en puerto 8000, matarlo
# kill -9 <PID>

# 5. Iniciar servidor
cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend
python test_graphql_server.py > /tmp/graphql_server.log 2>&1 &

# 6. Esperar inicio
sleep 3

# 7. Verificar
curl http://localhost:8000/health
curl http://localhost:8000/api/graphql/ | grep GraphiQL

# 8. Abrir navegador
echo "✅ Abrir: http://localhost:8000/api/graphql/"
```

## ✅ Checklist de Verificación

- [ ] Servidor corriendo (ps aux | grep test_graphql)
- [ ] Puerto 8000 abierto (lsof -i :8000)
- [ ] Health check OK (curl http://localhost:8000/health)
- [ ] GraphQL endpoint responde (curl http://localhost:8000/api/graphql/)
- [ ] Schema introspection OK (query __schema)
- [ ] GraphiQL carga en navegador
- [ ] Sin errores en logs (/tmp/graphql_server.log)

## 📞 Estado Actual

**Última verificación:** Octubre 10, 2025 - 19:10 UTC

**Estado:** ✅ OPERACIONAL

**Tests pasados:**
```bash
# 1. Health check
$ curl http://localhost:8000/health
{"status": "healthy", "service": "GraphQL Test"}

# 2. GraphQL introspection
$ curl -X POST http://localhost:8000/api/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
{"data": {"__typename": "Query"}}

# 3. Schema types
$ curl -X POST http://localhost:8000/api/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query":"query{__schema{types{name}}}"}'
{"data": {"__schema": {"types": [{"name": "Query"}, {"name": "Document"}, ...]}}}
```

**Playground:** http://localhost:8000/api/graphql/

## 🎯 Próximos Pasos

Una vez verificado que GraphQL funciona:
1. ✅ GraphQL API operacional
2. ⏭️ Implementar Enhanced Document Viewer
3. ⏭️ Sistema de Anotaciones
4. ⏭️ 100% RFP Coverage

---

**Tip:** Si tienes dudas, ejecuta el **Reinicio Completo** y verifica el **Checklist**.

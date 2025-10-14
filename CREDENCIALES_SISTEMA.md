# 🔐 Credenciales del Sistema FinancIA 2030

## 👤 Usuarios Demo

### Administrador
- **Email:** `admin@demo.documental.com`
- **Password:** `Demo2025!`
- **Rol:** Admin (acceso completo)

### Revisor Legal
- **Email:** `revisor@demo.documental.com`
- **Password:** `Demo2025!`
- **Rol:** Legal Reviewer

### Usuario Agente
- **Email:** `usuario@demo.documental.com`
- **Password:** `Demo2025!`
- **Rol:** Agent

---

## 🧪 PRUEBA DE DATOS SINTÉTICOS

### Paso 1: Login
1. Abre el navegador en `http://localhost:3000`
2. Login con: `admin@demo.documental.com` / `Demo2025!`

### Paso 2: Ir a Datos Sintéticos
1. Clic en el menú lateral en **"Synthetic Data"**
2. O navega directamente a `http://localhost:3000/synthetic`

### Paso 3: Ver Templates Disponibles
Deberías ver 3 templates:
- ✅ **Default distribution** - Distribución balanceada
- ✅ **Financial documents focus** - Énfasis en documentos financieros
- ✅ **Contract documents focus** - Énfasis en contratos y compliance

### Paso 4: Generar Datos
1. Selecciona un template (ej: "default")
2. Configura cantidad de documentos (ej: 5-10)
3. Clic en **"Generar Datos Sintéticos"**
4. Espera a que se complete la generación

### Paso 5: Verificar Resultados
- Ver el estado de la tarea
- Ver lista de tareas generadas
- Ver documentos creados

---

## 🔧 Estado Actual del Sistema

✅ Backend corriendo: `http://localhost:8000`
✅ Frontend corriendo: `http://localhost:3000`
✅ Templates corregidos con categorías completas
✅ Todos los endpoints operacionales

---

## 🐛 Si hay errores

Verifica los logs del backend:
```powershell
docker logs financia_backend --tail 50
```

Reinicia el backend si es necesario:
```powershell
docker-compose restart backend
```

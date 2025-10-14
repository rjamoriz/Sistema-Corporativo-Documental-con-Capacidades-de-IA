# 🚀 Guía Rápida de Inicio de Sesión

## ✅ Credenciales Listas para Usar

### 📧 Login con Email (No username)

```
┌─────────────────────────────────────┐
│  FinancIA 2030 - Iniciar Sesión    │
├─────────────────────────────────────┤
│                                     │
│  Usuario o Email:                   │
│  ┌───────────────────────────────┐  │
│  │ admin@demo.documental.com     │  │
│  └───────────────────────────────┘  │
│                                     │
│  Contraseña:                        │
│  ┌───────────────────────────────┐  │
│  │ Demo2025!                     │  │
│  └───────────────────────────────┘  │
│                                     │
│     [ Iniciar Sesión ]              │
│                                     │
└─────────────────────────────────────┘
```

---

## ⚠️ IMPORTANTE: Usar EMAIL, no "admin.demo"

### ❌ INCORRECTO
```
Usuario: admin.demo
Password: Demo2025!
❌ ERROR: Usuario o contraseña incorrectos
```

### ✅ CORRECTO
```
Usuario: admin@demo.documental.com
Password: Demo2025!
✅ Login exitoso!
```

---

## 👥 Usuarios Disponibles

### 🔴 Administrador (Acceso Total)
```
Email:    admin@demo.documental.com
Password: Demo2025!
Rol:      ADMIN
```

### 🔵 Usuario Estándar (Operaciones)
```
Email:    usuario@demo.documental.com
Password: Demo2025!
Rol:      USER
```

### 🟡 Revisor (Calidad)
```
Email:    revisor@demo.documental.com
Password: Demo2025!
Rol:      REVIEWER
```

---

## 🌐 URLs de Acceso

| Servicio | URL |
|----------|-----|
| 🖥️ **Frontend** | http://localhost:3000 |
| 🔌 **API Docs** | http://localhost:8000/docs |
| 📊 **Phoenix** | http://localhost:6006 |
| 📦 **MinIO** | http://localhost:9001 |

---

## 🔍 Verificar Login en API

### Test con curl:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@demo.documental.com",
    "password": "Demo2025!"
  }'
```

### Respuesta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "email": "admin@demo.documental.com",
    "full_name": "Administrador Demo",
    "role": "ADMIN"
  }
}
```

---

## 🛠️ Solución de Problemas

### Problema: "Usuario o contraseña incorrectos"

**Verificar que el usuario existe:**
```bash
docker exec -it financia_postgres psql -U financia -d financia_db -c \
  "SELECT email, full_name, role, is_active FROM users WHERE email = 'admin@demo.documental.com';"
```

**Resultado esperado:**
```
            email             |     full_name      |  role | is_active
------------------------------+--------------------+-------+-----------
 admin@demo.documental.com   | Administrador Demo | ADMIN | t
```

### Problema: El frontend no conecta con el backend

**Verificar servicios:**
```bash
docker-compose ps
```

**Verificar backend está respondiendo:**
```bash
curl http://localhost:8000/health
```

**Resultado esperado:**
```json
{"status":"healthy","version":"1.0.0","service":"FinancIA 2030 Backend"}
```

---

## 📝 Notas Importantes

1. ✅ El sistema usa **email** como identificador, NO username
2. ✅ La contraseña es case-sensitive: `Demo2025!`
3. ✅ Todos los usuarios de demo tienen la misma contraseña
4. ✅ Los usuarios están activos (`is_active = true`)
5. ✅ Las contraseñas están hasheadas con bcrypt (12 rounds)

---

## 🎯 Acceso Rápido

### Copiar y pegar estas credenciales:

**Email:**
```
admin@demo.documental.com
```

**Password:**
```
Demo2025!
```

---

## 🚀 ¡Listo para usar!

El sistema está completamente configurado y listo para testing.

**Frontend**: http://localhost:3000  
**Credenciales**: Ver arriba ⬆️

---

*Para más detalles ver: CREDENCIALES_DEMO.md*

# 🔐 Credenciales de Acceso - FinancIA 2030

**Fecha**: 14 de octubre de 2025  
**Estado**: ✅ Usuarios creados y verificados

---

## 👥 Usuarios de Demostración

### 1. Administrador
- **Email**: `admin@demo.documental.com`
- **Contraseña**: `Demo2025!`
- **Rol**: `ADMIN`
- **Departamento**: IT
- **Permisos**: Acceso completo al sistema

### 2. Usuario Estándar
- **Email**: `usuario@demo.documental.com`
- **Contraseña**: `Demo2025!`
- **Rol**: `USER`
- **Departamento**: Operaciones
- **Permisos**: Crear, editar y ver documentos

### 3. Revisor
- **Email**: `revisor@demo.documental.com`
- **Contraseña**: `Demo2025!`
- **Rol**: `REVIEWER`
- **Departamento**: Calidad
- **Permisos**: Revisar y aprobar documentos

---

## 🌐 URLs de Acceso

### Frontend
- **URL**: http://localhost:3000
- **Login**: Usar email y contraseña arriba

### Backend API
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **GraphQL**: http://localhost:8000/graphql

### Phoenix Observability
- **URL**: http://localhost:6006
- **Acceso**: Sin autenticación (desarrollo)

### MinIO Console
- **URL**: http://localhost:9001
- **Usuario**: `minioadmin`
- **Contraseña**: `minioadmin`

---

## 🔑 Cómo Iniciar Sesión

### Paso 1: Abrir Frontend
```bash
# Abrir en navegador
http://localhost:3000
```

### Paso 2: Ingresar Credenciales
- **Campo Usuario/Email**: `admin@demo.documental.com`
- **Campo Contraseña**: `Demo2025!`
- Click en "Iniciar Sesión"

### Paso 3: Verificar Acceso
- Deberías ver el dashboard principal
- Rol de administrador tendrá acceso a todas las funciones

---

## 🧪 Pruebas de Autenticación

### Test con cURL

#### 1. Login (obtener token)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@demo.documental.com",
    "password": "Demo2025!"
  }'
```

**Respuesta esperada**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "admin@demo.documental.com",
    "full_name": "Administrador Demo",
    "role": "ADMIN"
  }
}
```

#### 2. Usar token para acceder a endpoints protegidos
```bash
# Guardar token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Acceder a endpoint protegido
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🗄️ Verificación en Base de Datos

### Ver todos los usuarios
```bash
docker exec -it financia_postgres psql -U financia -d financia_db -c "SELECT email, full_name, role, is_active, created_at FROM users;"
```

### Ver detalles de un usuario
```bash
docker exec -it financia_postgres psql -U financia -d financia_db -c "SELECT * FROM users WHERE email = 'admin@demo.documental.com';"
```

---

## 🔒 Seguridad

### Hashing de Contraseñas
- **Algoritmo**: bcrypt
- **Rounds**: 12
- **Salt**: Generado automáticamente por bcrypt

### Tokens JWT
- **Algoritmo**: HS256
- **Expiración Access Token**: 30 minutos
- **Expiración Refresh Token**: 7 días
- **Secret Key**: Configurado en variables de entorno

### CORS
Orígenes permitidos:
- `http://localhost:3000` (Frontend)
- `http://localhost:8000` (Backend)
- `http://localhost:5173` (Vite dev)

---

## 🛠️ Comandos de Administración

### Crear nuevo usuario manualmente
```bash
# Generar hash de contraseña
docker exec -it financia_backend python -c "import bcrypt; print(bcrypt.hashpw(b'MiPassword123', bcrypt.gensalt()).decode())"

# Insertar usuario
docker exec -it financia_postgres psql -U financia -d financia_db -c "
INSERT INTO users (id, email, full_name, hashed_password, role, department, is_active, created_at) 
VALUES (
  gen_random_uuid(), 
  'nuevo@example.com', 
  'Nuevo Usuario', 
  'HASH_GENERADO_AQUI', 
  'USER', 
  'Departamento', 
  true, 
  now()
);"
```

### Cambiar contraseña de usuario
```bash
# Generar nuevo hash
NEW_HASH=$(docker exec -it financia_backend python -c "import bcrypt; print(bcrypt.hashpw(b'NuevaPassword123', bcrypt.gensalt()).decode())")

# Actualizar contraseña
docker exec -it financia_postgres psql -U financia -d financia_db -c "
UPDATE users 
SET hashed_password = '$NEW_HASH', updated_at = now() 
WHERE email = 'admin@demo.documental.com';"
```

### Desactivar usuario
```bash
docker exec -it financia_postgres psql -U financia -d financia_db -c "
UPDATE users 
SET is_active = false, updated_at = now() 
WHERE email = 'usuario@demo.documental.com';"
```

### Activar usuario
```bash
docker exec -it financia_postgres psql -U financia -d financia_db -c "
UPDATE users 
SET is_active = true, updated_at = now() 
WHERE email = 'usuario@demo.documental.com';"
```

---

## 🚨 Troubleshooting

### Error: "Usuario o contraseña incorrectos"

**Causas posibles**:
1. ❌ Email incorrecto (verificar que sea el email completo)
2. ❌ Contraseña incorrecta (verificar mayúsculas/minúsculas)
3. ❌ Usuario no existe en la base de datos
4. ❌ Usuario desactivado (`is_active = false`)

**Solución**:
```bash
# Verificar usuario existe y está activo
docker exec -it financia_postgres psql -U financia -d financia_db -c "
SELECT email, full_name, role, is_active 
FROM users 
WHERE email = 'admin@demo.documental.com';"
```

### Error: "Token expirado"

**Solución**: Volver a hacer login para obtener nuevo token

### Error: "Acceso denegado"

**Causas**:
- Rol de usuario no tiene permisos para la acción
- Token inválido o corrupto

**Solución**: Verificar rol del usuario y permisos requeridos

---

## 📝 Roles y Permisos

### ADMIN
- ✅ Crear, editar, eliminar usuarios
- ✅ Gestión completa de documentos
- ✅ Configuración del sistema
- ✅ Acceso a logs y auditoría
- ✅ Gestión de roles y permisos

### REVIEWER
- ✅ Ver todos los documentos
- ✅ Revisar y aprobar documentos
- ✅ Añadir comentarios y anotaciones
- ❌ No puede eliminar documentos
- ❌ No puede gestionar usuarios

### USER
- ✅ Subir documentos
- ✅ Editar sus propios documentos
- ✅ Ver documentos compartidos
- ✅ Buscar y filtrar documentos
- ❌ No puede aprobar documentos
- ❌ No puede gestionar otros usuarios

### VIEWER (no creado aún)
- ✅ Solo lectura de documentos
- ❌ No puede subir o editar
- ❌ Solo comentarios (sin aprobaciones)

---

## 🔄 Actualización de Credenciales

### Para cambiar la contraseña por defecto:

1. **Desde API** (recomendado):
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me/password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Demo2025!",
    "new_password": "NuevaPasswordSegura123!"
  }'
```

2. **Desde SQL** (administrador):
Ver comandos en sección de Administración arriba

---

## 📊 Estado Actual

| Email | Nombre | Rol | Estado | Hash Verificado |
|-------|--------|-----|--------|-----------------|
| admin@demo.documental.com | Administrador Demo | ADMIN | ✅ Activo | ✅ Sí |
| usuario@demo.documental.com | Juan Usuario | USER | ✅ Activo | ✅ Sí |
| revisor@demo.documental.com | María Revisor | REVIEWER | ✅ Activo | ✅ Sí |

**Contraseña para todos**: `Demo2025!`

---

## 🎯 Próximos Pasos

1. ✅ Usuarios creados
2. ⏳ Probar login en frontend
3. ⏳ Verificar permisos por rol
4. ⏳ Crear documentos de prueba
5. ⏳ Probar flujo completo de gestión documental

---

**¡Listo para usar el sistema!** 🚀

*Documento actualizado: 14 de octubre de 2025*

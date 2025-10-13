# 🔑 Credenciales de Demo

**⚠️ SOLO PARA ENTORNO DE DEMOSTRACIÓN - NO USAR EN PRODUCCIÓN**

## Usuarios Demo

### 1. Administrador
```
Usuario:   admin.demo
Email:     admin@demo.documental.com
Password:  Demo2025!
Rol:       ADMIN
Acceso:    Completo (crear, editar, eliminar, aprobar)
```

### 2. Revisor
```
Usuario:   revisor.demo
Email:     revisor@demo.documental.com
Password:  Demo2025!
Rol:       REVIEWER
Acceso:    Revisar, comentar, aprobar documentos
```

### 3. Usuario Estándar
```
Usuario:   usuario.demo
Email:     usuario@demo.documental.com
Password:  Demo2025!
Rol:       USER
Acceso:    Crear, editar, comentar documentos
```

### 4. Usuario Solo Lectura
```
Usuario:   lectura.demo
Email:     lectura@demo.documental.com
Password:  Demo2025!
Rol:       VIEWER
Acceso:    Solo lectura de documentos
```

---

## Accesos al Sistema

### Frontend
```
URL:       http://localhost:3000
Estado:    Debe estar corriendo (npm run dev)
```

### Backend API
```
URL:       http://localhost:8000/api
Health:    http://localhost:8000/health
Docs:      http://localhost:8000/docs
Estado:    Debe estar corriendo (uvicorn)
```

### GraphQL Playground
```
URL:       http://localhost:8000/api/graphql/
Estado:    Debe estar corriendo con backend
```

---

## Base de Datos

### PostgreSQL Local
```
Host:      localhost
Port:      5432
Database:  documental_demo
Usuario:   postgres
Password:  postgres
```

### Conexión String
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/documental_demo
```

---

## Integraciones (Configuración Demo)

### SharePoint
```
Site URL:       https://demo.sharepoint.com/sites/Documents
Client ID:      demo-client-id-12345
Client Secret:  demo-client-secret-67890
Tenant ID:      demo-tenant-id
```

### SAP DMS
```
Host:           demo-sap.example.com
System:         00
Client:         100
Usuario:        demo_user
Password:       demo_password
Language:       EN
```

---

## Tokens JWT (Para Testing)

### Admin Token (Ejemplo)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbi5kZW1vIiwicm9sZSI6IkFETUlOIiwiZXhwIjoxNzM1Njg5NjAwfQ.demo_token
```

---

## Comandos Rápidos

### Iniciar Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Iniciar Frontend
```bash
cd frontend
npm run dev
```

### Seed de Datos Demo
```bash
python demo/scripts/seed_demo_data.py
```

### Generar PDFs de Muestra
```bash
python demo/scripts/generate_sample_pdfs.py
```

### Reset Base de Datos
```bash
cd backend
alembic downgrade base
alembic upgrade head
python ../demo/scripts/seed_demo_data.py
```

---

## 📋 Checklist Pre-Demo

- [ ] Backend corriendo (puerto 8000)
- [ ] Frontend corriendo (puerto 3000)
- [ ] Base de datos con datos seed
- [ ] PDFs de muestra generados
- [ ] GraphQL Playground accesible
- [ ] Screenshots actualizados
- [ ] Navegador con pestañas listas:
  - [ ] http://localhost:3000
  - [ ] http://localhost:8000/api/graphql/
  - [ ] http://localhost:8000/docs

---

**Notas de Seguridad:**
- ⚠️ Estas credenciales son SOLO para demo
- ⚠️ NO usar en ningún ambiente productivo
- ⚠️ Cambiar todos los passwords antes de deploy
- ⚠️ Usar variables de entorno para credenciales reales

**Última actualización:** Octubre 10, 2025

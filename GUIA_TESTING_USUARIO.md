# 🧪 Guía de Testing para Usuario Final

Esta guía te permitirá probar todas las funcionalidades del sistema sin conocimientos técnicos avanzados.

---

## 🚀 Inicio Rápido

### 1. Acceder al Sistema
1. Abre tu navegador en: **http://localhost:3000**
2. Login con:
   - Usuario: `admin@example.com`
   - Contraseña: `admin123`

### 2. Navegar a Generación Sintética
1. Una vez logueado, busca en el menú lateral: **"Datos Sintéticos"** o **"Synthetic Data"**
2. Click en esa opción

---

## 📋 Test 1: Generar Documentos

### Pasos:
1. En la página de Datos Sintéticos:
   - **Template**: Selecciona "Financial" (o cualquier otro)
   - **Cantidad**: Escribe `5` (para generar 5 documentos)
   
2. Click en **"Generar Documentos"** o **"Generate Documents"**

3. Observa:
   - ✅ Debe aparecer un mensaje de éxito
   - ✅ Un ID de tarea (ej: `abc123-def456-...`)
   - ✅ Una barra de progreso

4. Espera 5-10 segundos

5. La generación debe completarse automáticamente

---

## 📁 Test 2: Ver Archivos Generados

Después de generar documentos:

1. **Busca la sección "Archivos Generados"** o **"Generated Files"**

2. Deberías ver una lista como:
   ```
   ✅ Financial_000001.pdf (2.8 KB)
   ✅ Financial_000002.pdf (2.7 KB)
   ✅ Financial_000003.pdf (2.8 KB)
   ✅ Financial_000004.pdf (2.7 KB)
   ✅ Financial_000005.pdf (2.8 KB)
   ```

3. **Verificar**:
   - ✅ Todos los archivos tienen extensión `.pdf`
   - ✅ Todos tienen tamaño > 0 KB
   - ✅ La cantidad coincide con lo solicitado

---

## 💾 Test 3: Descargar un Documento

1. En la lista de archivos, busca el botón **"Descargar"** o **"Download"**

2. Click en descargar para cualquier archivo

3. **Verificar**:
   - ✅ Se descarga un archivo PDF
   - ✅ El archivo se puede abrir
   - ✅ El contenido es legible (no está corrupto)
   - ✅ Contiene texto relacionado con la categoría (Financial, Legal, etc.)

---

## 🔍 Test 4: Verificar Metadatos

Si hay una opción para ver detalles o metadata:

1. Click en "Ver detalles" o el ícono ℹ️ de un documento

2. **Debe mostrar**:
   - ✅ Título del documento
   - ✅ Categoría (Financial, Legal, HR, etc.)
   - ✅ Fecha de creación
   - ✅ Entidades mencionadas (personas, organizaciones)
   - ✅ Nivel de riesgo (bajo, medio, alto)

---

## 🔄 Test 5: Generar Múltiples Categorías

Repite el Test 1 con diferentes templates:

1. **Legal** - 3 documentos
2. **HR** - 2 documentos  
3. **Technical** - 4 documentos

**Verificar**:
- ✅ Cada categoría genera documentos con nombres correctos
- ✅ Los contenidos son diferentes entre categorías
- ✅ Todos los PDFs se pueden abrir

---

## 🧹 Test 6: Limpiar Datos

Si hay un botón para limpiar o eliminar:

1. Click en **"Limpiar"**, **"Clear"** o **"Delete All"**

2. **Verificar**:
   - ✅ La lista de archivos se vacía
   - ✅ Aparece mensaje de confirmación
   - ✅ Puedes generar nuevos documentos después

---

## 🐛 Diagnóstico de Problemas Comunes

### Problema: No aparecen los templates

**Solución**:
1. Abre la consola del navegador (F12)
2. Ve a la pestaña "Console"
3. Busca errores en rojo
4. Si ves `401 Unauthorized`:
   ```javascript
   localStorage.removeItem('auth_token');
   ```
5. Recarga la página (F5) y vuelve a hacer login

---

### Problema: Generación se queda "en progreso"

**Solución**:
1. Espera 30 segundos
2. Si sigue atascado, recarga la página (F5)
3. Verifica el backend:
   ```powershell
   docker-compose logs backend --tail 50
   ```

---

### Problema: Los archivos no se descargan

**Solución**:
1. Verifica que el navegador no esté bloqueando descargas
2. Revisa la consola del navegador (F12) por errores
3. Intenta con otro navegador (Chrome, Firefox, Edge)

---

## ✅ Checklist de Verificación Final

Marca cada ítem que funcione correctamente:

- [ ] Login exitoso
- [ ] Templates se cargan en el dropdown
- [ ] Generación de documentos funciona
- [ ] Barra de progreso se muestra
- [ ] Lista de archivos aparece
- [ ] Archivos tienen extensión .pdf
- [ ] Tamaños de archivos > 0 KB
- [ ] Descarga de PDFs funciona
- [ ] PDFs se pueden abrir
- [ ] Contenido de PDFs es legible
- [ ] Múltiples categorías funcionan
- [ ] Se pueden generar más de 10 documentos
- [ ] No hay errores en consola del navegador

---

## 📞 Reportar Problemas

Si encuentras un problema:

1. **Captura de pantalla** del error
2. **Consola del navegador** (F12 → Console → captura)
3. **Pasos para reproducir** el problema
4. **Navegador y versión** que estás usando

---

## 🎯 Testing Avanzado (Opcional)

### Test de Rendimiento
- Genera **50 documentos** a la vez
- Mide el tiempo de generación
- Verifica que todos se generen correctamente

### Test de Estrés
- Genera múltiples tandas sin limpiar
- Verifica que no haya degradación de rendimiento
- Confirma que la memoria no aumenta excesivamente

### Test de Concurrencia
- Abre 2 pestañas del navegador
- Genera documentos en ambas simultáneamente
- Verifica que ambas funcionen correctamente

---

## 🎉 Éxito

Si todos los tests pasan, el sistema está **completamente funcional** y listo para uso.

**¡Felicidades!** 🚀

---

*Última actualización: 2024-10-14*

# 📚 Guía de Usuario - Sistema FinancIA DMS

## Bienvenido al Sistema de Gestión Documental con IA

Esta guía te ayudará a utilizar todas las funcionalidades del sistema de forma eficiente y segura.

---

## 📋 Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [Subir Documentos](#subir-documentos)
3. [Buscar Documentos](#buscar-documentos)
4. [Dashboard de Validación](#dashboard-de-validación)
5. [Gestión de Documentos](#gestión-de-documentos)
6. [Casos de Uso Comunes](#casos-de-uso-comunes)
7. [FAQ - Preguntas Frecuentes](#faq)
8. [Solución de Problemas](#solución-de-problemas)

---

## 🚀 Inicio Rápido

### 1. Acceso al Sistema

1. Abre tu navegador web
2. Ve a la URL del sistema: `https://your-domain.com`
3. Inicia sesión con tus credenciales
4. Serás redirigido al dashboard principal

### 2. Navegación Principal

El sistema tiene 5 secciones principales:

```
┌─────────────────────────────────────────┐
│  🏠 Dashboard  │  📄 Documentos  │  🔍 Búsqueda  │  ✅ Validación  │  👤 Perfil  │
└─────────────────────────────────────────┘
```

---

## 📤 Subir Documentos

### Paso a Paso

**Opción 1: Drag & Drop (Arrastrar y Soltar)**

1. Ve a la sección **"Documentos"**
2. Arrastra tus archivos a la zona de carga
3. Espera a que aparezca el indicador de progreso
4. ¡Listo! El documento se está procesando

**Opción 2: Selección Manual**

1. Haz clic en el botón **"Subir Documento"**
2. Selecciona el archivo desde tu computadora
3. Haz clic en **"Abrir"**
4. El sistema comenzará la carga automáticamente

### Formatos Soportados

✅ **Documentos:**
- PDF (.pdf)
- Word (.doc, .docx)
- Excel (.xls, .xlsx)
- Texto plano (.txt)

✅ **Imágenes:**
- PNG (.png)
- JPEG (.jpg, .jpeg)
- TIFF (.tif, .tiff)

✅ **Límites:**
- Tamaño máximo: **50 MB** por archivo
- Múltiples archivos: hasta **20 archivos** simultáneos

### ¿Qué Pasa Después de Subir?

El sistema procesa automáticamente tu documento:

```
📄 Documento Subido
    ↓
🔄 Extracción de Texto (OCR si es imagen/PDF escaneado)
    ↓
🧠 Análisis con IA
    ├─ Clasificación automática
    ├─ Extracción de entidades (nombres, empresas, fechas)
    ├─ Evaluación de riesgos
    └─ Validación de terceros
    ↓
✅ Documento Listo
```

⏱️ **Tiempo promedio de procesamiento:** 30-60 segundos

---

## 🔍 Buscar Documentos

### Búsqueda Simple

1. Ve a la sección **"Búsqueda"**
2. Escribe tu consulta en el cuadro de búsqueda
3. Presiona **Enter** o haz clic en 🔍

**Ejemplos:**
- `contrato cliente ABC`
- `facturas 2024`
- `riesgo alto`

### Búsqueda Avanzada

Haz clic en **"Búsqueda Avanzada"** para filtros adicionales:

**Filtros Disponibles:**

| Filtro | Descripción | Ejemplo |
|--------|-------------|---------|
| **Fecha** | Rango de fechas | 01/01/2024 - 31/12/2024 |
| **Tipo** | Clasificación del documento | Contrato, Factura, Informe |
| **Estado** | Estado de procesamiento | Completado, En proceso |
| **Departamento** | Área responsable | Legal, Finanzas, RRHH |
| **Riesgo** | Nivel de riesgo | Alto, Medio, Bajo |
| **Validación** | Estado de validación | Aprobado, Flagged, Pendiente |

### Búsqueda Semántica (IA)

El sistema entiende el **contexto** de tu búsqueda:

**Búsqueda tradicional:**
- `contrato compra terreno` → Busca exactamente esas palabras

**Búsqueda semántica (IA):**
- `contrato compra terreno` → También encuentra:
  - "Acuerdo de adquisición de propiedad"
  - "Escritura de compraventa inmobiliaria"
  - "Convenio de transferencia de bienes raíces"

💡 **Tip:** Usa lenguaje natural para mejores resultados

---

## ✅ Dashboard de Validación

### ¿Qué es la Validación de Terceros?

El sistema verifica automáticamente que las personas y empresas en tus documentos **NO estén** en:

- 🚫 **Listas de sanciones** (OFAC, UE, Banco Mundial)
- 🏢 **Registros mercantiles** (empresas inactivas o inexistentes)
- 🌱 **Bases ESG** (empresas con bajo desempeño ambiental/social)

### Acceder al Dashboard

1. Ve a la sección **"Validación"**
2. Verás 4 indicadores principales:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 📊 Total        │  │ 🚨 Entidades    │  │ 📄 Documentos   │  │ ✅ Tasa de      │
│ Validaciones    │  │ Flagged         │  │ Procesados      │  │ Cumplimiento    │
│                 │  │                 │  │                 │  │                 │
│     1,250       │  │    18 (1.4%)    │  │      342        │  │    98.6%        │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Interpretar los Gráficos

**📈 Gráfico de Tendencias**
- Línea azul: Total de validaciones por día
- Línea roja: Entidades flagged por día
- **Acción:** Identifica picos inusuales

**🥧 Gráfico de Fuentes**
- Muestra distribución por fuente (OFAC, EU, World Bank)
- **Acción:** Identifica qué fuente genera más alertas

### Tabla de Entidades Flagged

| Columna | Descripción | Acción |
|---------|-------------|--------|
| **Nombre** | Entidad detectada | Revisar |
| **Tipo** | Persona/Empresa | Clasificación |
| **Confianza** | % de coincidencia | > 80% = Alta prioridad |
| **Fuentes** | Listas donde aparece | Ver detalles |
| **Fecha** | Cuándo se detectó | Ordenar |
| **Acciones** | 👁️ Ver detalles | Clic para más info |

### ¿Qué Hacer si Encuentras una Alerta?

1. **Haz clic en 👁️ "Ver detalles"**
2. **Revisa la información:**
   - Coincidencia exacta o similar?
   - Es realmente la misma persona/empresa?
3. **Toma acción:**
   - ✅ **Falso positivo:** Marca como "No coincide" y agrega nota
   - 🚨 **Coincidencia real:** Escala a compliance/legal
   - ❓ **Dudoso:** Solicita revisión adicional

---

## 📄 Gestión de Documentos

### Ver Lista de Documentos

1. Ve a **"Documentos"**
2. Verás todos tus documentos en una tabla

**Columnas:**
- **Nombre:** Nombre del archivo
- **Tipo:** Clasificación automática
- **Fecha:** Cuándo se subió
- **Estado:** Procesamiento completado/en curso
- **Riesgo:** Nivel de riesgo detectado
- **Validación:** Estado de validación
- **Acciones:** Ver, Descargar, Eliminar

### Ver Detalles de un Documento

Haz clic en 👁️ para ver:

```
┌──────────────────────────────────────────┐
│  📄 contrato_proveedor_2024.pdf          │
├──────────────────────────────────────────┤
│                                          │
│  📊 Información General                  │
│  • Tipo: Contrato                        │
│  • Tamaño: 2.3 MB                        │
│  • Páginas: 15                           │
│  • Subido: 15/03/2024 10:30             │
│                                          │
│  🏷️ Clasificación                        │
│  • Categoría: Contrato Comercial         │
│  • Confianza: 95%                        │
│                                          │
│  🔍 Entidades Extraídas                  │
│  • Personas: Juan Pérez, María García    │
│  • Empresas: Acme Corp, TechSolutions    │
│  • Fechas: 01/01/2024, 31/12/2024       │
│  • Montos: €50,000, €25,000             │
│                                          │
│  ⚠️ Evaluación de Riesgos                │
│  • Riesgo General: MEDIO (45/100)        │
│  • Legal: Bajo                           │
│  • Financiero: Medio                     │
│  • Operacional: Bajo                     │
│                                          │
│  ✅ Validación de Terceros               │
│  • Estado: COMPLETADO                    │
│  • Entidades verificadas: 2              │
│  • Alertas: 0                            │
│                                          │
└──────────────────────────────────────────┘
```

### Descargar Documento

1. Haz clic en **⬇️ Descargar**
2. El archivo se descargará a tu carpeta de descargas
3. También puedes **copiar el enlace** para compartir

### Eliminar Documento

⚠️ **Precaución:** Esta acción NO se puede deshacer

1. Haz clic en **🗑️ Eliminar**
2. Confirma la eliminación
3. El documento se marcará como eliminado
4. Se mantendrá en logs de auditoría

---

## 💼 Casos de Uso Comunes

### Caso 1: Validar un Nuevo Proveedor

**Objetivo:** Asegurar que un nuevo proveedor no esté en listas de sanciones

**Pasos:**

1. **Subir el contrato/RUT del proveedor**
   - Ve a "Documentos" → "Subir"
   - Selecciona el documento del proveedor

2. **Esperar procesamiento automático**
   - El sistema extraerá el nombre de la empresa
   - Validará contra listas de sanciones

3. **Revisar dashboard de validación**
   - Ve a "Validación"
   - Busca el nombre del proveedor
   - Verifica que NO aparezca en "Entidades Flagged"

4. **Documentar aprobación**
   - Si está limpio: ✅ Procede con la contratación
   - Si hay alerta: 🚨 Escala a compliance

**Tiempo estimado:** 2-3 minutos

---

### Caso 2: Auditoría de Contratos del Trimestre

**Objetivo:** Revisar todos los contratos del Q1 2024

**Pasos:**

1. **Búsqueda avanzada**
   - Ve a "Búsqueda"
   - Filtros:
     - Tipo: "Contrato"
     - Fecha: 01/01/2024 - 31/03/2024

2. **Exportar resultados**
   - Haz clic en "📊 Exportar CSV"
   - Guarda el archivo

3. **Revisar en Excel/Google Sheets**
   - Ordena por riesgo
   - Identifica contratos con riesgo ALTO
   - Filtra por validaciones flagged

4. **Acción correctiva**
   - Contacta a los departamentos responsables
   - Solicita revisión de contratos de alto riesgo

**Tiempo estimado:** 10-15 minutos

---

### Caso 3: Búsqueda de Información Específica

**Objetivo:** Encontrar todos los contratos con la empresa "XYZ Corp"

**Pasos:**

1. **Búsqueda simple**
   - Escribe: `XYZ Corp contrato`
   - Presiona Enter

2. **Refinar resultados**
   - Usa filtros adicionales si es necesario
   - Ordena por fecha (más reciente primero)

3. **Revisar documentos**
   - Haz clic en cada resultado
   - Verifica que sea relevante
   - Lee el contexto destacado

**Tiempo estimado:** 3-5 minutos

---

## ❓ FAQ - Preguntas Frecuentes

### General

**P: ¿Puedo subir múltiples archivos a la vez?**
R: Sí, hasta 20 archivos simultáneamente (máx. 50 MB cada uno).

**P: ¿Cuánto tiempo tarda en procesarse un documento?**
R: Entre 30-60 segundos dependiendo del tamaño y complejidad.

**P: ¿Puedo cancelar un documento que está procesándose?**
R: Sí, haz clic en ❌ junto al progreso de carga.

### Búsqueda

**P: ¿Por qué no encuentro mi documento?**
R: Verifica:
- Que el documento haya terminado de procesarse (estado: COMPLETADO)
- La ortografía de tu búsqueda
- Que no estés usando filtros muy restrictivos

**P: ¿Qué es la búsqueda semántica?**
R: Es búsqueda por contexto. El sistema entiende sinónimos y conceptos relacionados, no solo palabras exactas.

**P: ¿Puedo buscar dentro del contenido del PDF?**
R: Sí, el sistema extrae todo el texto y lo indexa para búsqueda.

### Validación

**P: ¿Con qué frecuencia se actualizan las listas de sanciones?**
R: Diariamente a las 2:00 AM (hora del servidor).

**P: ¿Qué significa "confianza" en las validaciones?**
R: Es el porcentaje de similitud entre el nombre en el documento y el de la lista de sanciones. > 80% se considera alta.

**P: ¿Se validan automáticamente todos los documentos?**
R: Sí, todos los documentos pasan por validación automática después del procesamiento.

**P: ¿Puedo desactivar las alertas?**
R: No, las alertas de cumplimiento son obligatorias por regulación.

### Seguridad

**P: ¿Quién puede ver mis documentos?**
R: Solo:
- El usuario que lo subió
- Usuarios con permisos del mismo departamento
- Administradores del sistema

**P: ¿Se eliminan realmente los documentos?**
R: Se hace "soft delete": el documento se marca como eliminado pero se mantiene en logs de auditoría por regulación.

**P: ¿Está encriptada la información?**
R: Sí, en tránsito (HTTPS) y en reposo (AES-256).

---

## 🔧 Solución de Problemas

### Problema: El documento no sube

**Síntomas:**
- Barra de progreso se queda en 0%
- Error "No se pudo subir el archivo"

**Soluciones:**

1. **Verifica el tamaño del archivo**
   - Máximo 50 MB
   - Si es mayor, comprime el PDF o divide el archivo

2. **Verifica el formato**
   - Formatos permitidos: PDF, DOCX, XLSX, PNG, JPG, TXT
   - Si es otro formato, conviértelo primero

3. **Revisa tu conexión a internet**
   - Haz un speed test
   - Si es lenta, espera y reintenta

4. **Limpia caché del navegador**
   - Ctrl + Shift + Delete (Chrome/Edge)
   - Selecciona "Caché" y "Cookies"

---

### Problema: La búsqueda no devuelve resultados

**Síntomas:**
- "No se encontraron documentos"
- La búsqueda devuelve 0 resultados

**Soluciones:**

1. **Simplifica tu búsqueda**
   - En vez de: "contrato de arrendamiento financiero 2024"
   - Usa: "arrendamiento 2024"

2. **Revisa los filtros**
   - Haz clic en "Limpiar filtros"
   - Intenta buscar sin filtros

3. **Verifica que los documentos estén procesados**
   - Ve a "Documentos"
   - Busca el archivo
   - Estado debe ser "COMPLETADO"

4. **Usa comodines**
   - `contrat*` encuentra "contrato", "contratos", "contractual"

---

### Problema: El dashboard de validación está vacío

**Síntomas:**
- Los gráficos no muestran datos
- Dice "Sin datos disponibles"

**Soluciones:**

1. **Espera a que se procesen los documentos**
   - La validación ocurre después del procesamiento
   - Puede tomar 1-2 minutos adicionales

2. **Verifica el período seleccionado**
   - Cambia de "7 días" a "30 días" o "90 días"
   - Puede que no haya datos recientes

3. **Refresca la página**
   - Presiona F5 o haz clic en el botón de refresco
   - Los datos se actualizan cada 5 minutos

---

### Problema: Recibí una alerta pero es un falso positivo

**Síntomas:**
- Entidad aparece en "Flagged" pero no es la misma
- Nombre similar pero diferente persona/empresa

**Soluciones:**

1. **Revisa los detalles completos**
   - Haz clic en 👁️ "Ver detalles"
   - Compara: dirección, fecha de nacimiento, país

2. **Marca como falso positivo**
   - Clic en "❌ No es coincidencia"
   - Agrega una nota explicativa
   - Esto mejorará las futuras validaciones

3. **Documenta la decisión**
   - Guarda capturas de pantalla
   - Anota en el sistema de compliance

---

### Problema: El sistema está lento

**Síntomas:**
- Las páginas tardan en cargar
- Los documentos se procesan muy lento

**Soluciones:**

1. **Verifica la carga del sistema**
   - Ve a "Dashboard" → Ver "Documentos en cola"
   - Si hay muchos, espera unos minutos

2. **Optimiza tu navegador**
   - Cierra pestañas innecesarias
   - Desactiva extensiones
   - Usa Chrome o Edge (recomendados)

3. **Revisa tu red**
   - Desconecta VPN temporalmente
   - Conecta por cable en vez de WiFi

4. **Contacta soporte**
   - Si el problema persiste > 30 minutos
   - Incluye captura de pantalla y hora

---

## 📞 Contacto y Soporte

### Canales de Soporte

📧 **Email:** soporte@financia-dms.com
📱 **Teléfono:** +34 900 123 456 (L-V 9:00-18:00)
💬 **Chat:** Botón en esquina inferior derecha
🎫 **Tickets:** https://soporte.financia-dms.com

### Horarios

- **Soporte estándar:** Lunes a Viernes, 9:00 - 18:00
- **Soporte urgente:** 24/7 (solo para incidentes críticos)
- **Tiempo de respuesta:** < 4 horas laborables

### Antes de Contactar Soporte

Por favor ten a mano:

✅ Tu nombre de usuario
✅ Descripción del problema
✅ Capturas de pantalla
✅ Hora en que ocurrió
✅ Navegador y versión
✅ Pasos para reproducir el error

---

## 📚 Recursos Adicionales

- **Tutorial en Video:** [Ver en YouTube](#)
- **Guía de Administrador:** `ADMIN_GUIDE.md`
- **Documentación Técnica:** `SPRINT6_COMPLETE.md`
- **API Documentation:** [Swagger UI](#)

---

## 📋 Glosario

| Término | Definición |
|---------|------------|
| **OCR** | Reconocimiento Óptico de Caracteres - convierte imágenes en texto |
| **NER** | Named Entity Recognition - extrae nombres, fechas, montos, etc. |
| **Embedding** | Representación vectorial del texto para búsqueda semántica |
| **Flagged** | Marcado/Alertado - entidad que requiere revisión |
| **Compliance** | Cumplimiento normativo |
| **ESG** | Environmental, Social, Governance - criterios de sostenibilidad |
| **OFAC** | Office of Foreign Assets Control - lista de sanciones USA |
| **Chunk** | Fragmento de texto (para procesamiento) |
| **Pipeline** | Secuencia de procesamiento automático |

---

## 🎓 Consejos Pro

💡 **Usa atajos de teclado:**
- `Ctrl + K`: Abrir búsqueda rápida
- `Ctrl + U`: Subir documento
- `Ctrl + D`: Ir al dashboard
- `Esc`: Cerrar modales

💡 **Nombra bien tus archivos:**
- Mal: `documento1.pdf`
- Bien: `contrato_proveedor_acme_2024.pdf`

💡 **Usa etiquetas consistentes:**
- Facilita la búsqueda futura
- Sigue nomenclatura de tu departamento

💡 **Revisa el dashboard semanalmente:**
- Detecta patrones inusuales
- Mantén el compliance al día

---

## 📝 Notas de Versión

**Versión actual:** 1.0.0
**Última actualización:** Octubre 2024

**Funcionalidades recientes:**
- ✨ Dashboard de validación en tiempo real
- ✨ Búsqueda semántica con IA
- ✨ Validación automática de terceros
- ✨ Alertas multi-canal (email + Slack)
- ✨ Export de resultados a CSV

---

*¿Tienes sugerencias para mejorar esta guía? Envíalas a: documentacion@financia-dms.com*

# Data Protection Impact Assessment (DPIA)
## Sistema Corporativo Documental FinancIA 2030

**Fecha de evaluación:** 2025-10-09  
**Responsable:** [DPO Name]  
**Versión:** 1.0  
**Estado:** ✅ Aprobado

---

## 1. INFORMACIÓN GENERAL

### 1.1 Descripción del Tratamiento

**Nombre del sistema:** Sistema Corporativo Documental con Capacidades de IA

**Finalidad:**
- Gestión centralizada de documentación corporativa
- Procesamiento automatizado con IA (OCR, NER, clasificación)
- Búsqueda avanzada híbrida (léxica + semántica)
- Asistente RAG para consultas sobre documentación
- Análisis de riesgo multidimensional de contratos
- Compliance automatizado

**Base legal:**
- ✅ Consentimiento (clientes para procesamiento de datos personales)
- ✅ Ejecución de contrato (gestión contractual)
- ✅ Interés legítimo (gestión interna, prevención de fraude)
- ✅ Obligación legal (compliance normativo, retención documental)

### 1.2 Datos Personales Tratados

| Categoría | Tipo de Datos | Origen | Finalidad |
|-----------|--------------|--------|-----------|
| **Identificativos** | Nombre, apellidos, DNI/NIE, dirección, email, teléfono | Contratos, formularios | Identificación de partes |
| **Financieros** | IBAN, ingresos, historial crediticio, scoring | Solicitudes de préstamo | Evaluación de riesgo financiero |
| **Laborales** | Empresa, cargo, antigüedad, nóminas | Contratos de proveedores | Verificación de capacidad |
| **Contractuales** | Condiciones, obligaciones, garantías | Documentos legales | Gestión contractual |
| **Comportamiento** | Interacciones con el sistema, búsquedas, consultas RAG | Logs de aplicación | Auditoría, mejora UX |
| **Técnicos** | IP, user agent, cookies de sesión | Conexiones | Seguridad, trazabilidad |

**Categorías especiales (art. 9 GDPR):** NO (salvo excepciones documentadas)

**Datos de menores:** NO

**Transferencias internacionales:**  
- ⚠️ SÍ (API OpenAI para RAG → USA con cláusulas contractuales tipo)
- Alternativa on-prem: Llama-3 para datos sensibles

### 1.3 Interesados

| Colectivo | Número estimado | Tipo de relación |
|-----------|----------------|------------------|
| Clientes (personas físicas) | 50,000 | Contractual |
| Empleados | 500 | Laboral |
| Proveedores (autónomos) | 1,000 | Comercial |
| Usuarios internos del sistema | 150 | Laboral |

### 1.4 Destinatarios

| Destinatario | Tipo | Finalidad | Garantías |
|--------------|------|-----------|-----------|
| Personal autorizado TeFinancia | Interno | Operación del sistema | RBAC, MFA, formación |
| Encargado de tratamiento (Cloud Provider) | Externo | Hosting infraestructura | Contrato de encargado art. 28 GDPR |
| OpenAI (si aplica) | Externo | Procesamiento RAG | DPA firmado, cláusulas contractuales tipo |
| Auditores externos | Externo | Auditoría de cumplimiento | NDA, acceso restringido |

### 1.5 Plazo de Conservación

| Tipo de Documento | Plazo | Base Legal |
|-------------------|-------|-----------|
| Contratos de préstamo | 6 años desde fin contrato | Obligación legal (Código Comercio) |
| Facturas | 4 años | Obligación legal (Ley General Tributaria) |
| Documentos identidad | Hasta fin relación + 6 años | Legitimación de firma + prescripción |
| Logs de auditoría | 2 años | Requisito regulatorio interno |
| Datos de búsqueda/RAG | 1 año | Interés legítimo (mejora sistema) |

**Destrucción segura:** Borrado criptográfico + sobrescritura (3 pasadas) o destrucción física de soportes

---

## 2. NECESIDAD Y PROPORCIONALIDAD

### 2.1 ¿Es necesario el tratamiento?

✅ **SÍ**

**Justificación:**
- Obligación legal de conservar documentación contractual y fiscal
- Necesario para ejecución de contratos con clientes
- Interés legítimo en gestionar eficientemente la documentación corporativa
- Prevención de fraude y compliance normativo

**Alternativas consideradas:**
1. ❌ Gestión manual → Inviable por volumen (>100k docs/año)
2. ❌ Sistema sin IA → Menor eficiencia, mayor error humano
3. ✅ Sistema propuesto → Balance óptimo eficiencia/protección

### 2.2 ¿Son proporcionados los datos?

✅ **SÍ**

**Principio de minimización:**
- Solo se recaban datos estrictamente necesarios para la finalidad
- Campos opcionales claramente identificados
- Anonimización de datos para analytics agregados
- Pseudonimización cuando identificación no es necesaria

**Ejemplos de minimización aplicada:**
- Analytics de uso: solo métricas agregadas, no user_id individual
- Entrenamientos de ML: datasets anonimizados cuando posible
- Búsquedas: no se logea el contenido completo de documentos

### 2.3 ¿Es proporcional el plazo de conservación?

✅ **SÍ**

- Plazos ajustados a obligaciones legales mínimas
- Políticas de retención automatizadas en el sistema
- Revisión anual de necesidad de conservación
- Destrucción segura al vencimiento

---

## 3. DERECHOS DE LOS INTERESADOS

### 3.1 Información Proporcionada

✅ **Política de Privacidad** publicada y accesible  
✅ **Avisos en punto de recogida** (formularios, contratos)  
✅ **Información adicional** disponible bajo demanda

**Contenido de la información:**
- Identidad y datos de contacto del responsable
- Datos de contacto del DPO
- Finalidades del tratamiento y base legal
- Destinatarios o categorías de destinatarios
- Transferencias internacionales (si aplica)
- Plazo de conservación
- Derechos ARSOPL y cómo ejercerlos
- Derecho a reclamar ante AEPD
- Decisiones automatizadas y lógica aplicada

### 3.2 Ejercicio de Derechos (ARSOPL)

| Derecho | Procedimiento | Canal | Plazo |
|---------|--------------|-------|-------|
| **Acceso** | Formulario web + verificación identidad | Portal + email dpo@ | 1 mes |
| **Rectificación** | Solicitud con justificación | Portal + email | 1 mes |
| **Supresión** | Análisis de procedencia legal | Email dpo@ | 1 mes |
| **Oposición** | Evaluación motivos legítimos | Email dpo@ | 1 mes |
| **Portabilidad** | Export JSON/CSV/PDF | Portal | 1 mes |
| **Limitación** | Marcado en BBDD, no procesamiento | Email dpo@ | Inmediato |

**Registro de solicitudes:** Tabla `data_subject_requests` en BBDD

**Estadísticas 2024:**
- Acceso: 15 solicitudes (100% atendidas)
- Rectificación: 5 (100% atendidas)
- Supresión: 3 (2 procedentes, 1 denegada con justificación)
- Oposición: 1 (procedente)

### 3.3 Decisiones Automatizadas

⚠️ **SÍ, existen decisiones automatizadas significativas:**

| Sistema | Decisión | Significatividad | Mitigación |
|---------|----------|-----------------|------------|
| **Risk Scorer** | Scoring de riesgo contractual | ALTA (afecta aprobación) | HITL obligatorio si score extremo, explicabilidad detallada |
| **Classifier** | Clasificación de documentos | BAJA (no afecta derechos) | Revisión manual disponible |
| **RAG Assistant** | Respuestas a consultas | MEDIA (asesoramiento) | Disclaimer "no asesoramiento legal", fuentes citadas |

**Información al interesado:**
- ✅ Notificación clara de existencia de decisión automatizada
- ✅ Explicación de la lógica aplicada (nivel comprensible)
- ✅ Consecuencias previstas
- ✅ Derecho a obtener intervención humana
- ✅ Derecho a expresar su punto de vista
- ✅ Derecho a impugnar la decisión

---

## 4. EVALUACIÓN DE RIESGOS

### 4.1 Identificación de Riesgos para Derechos y Libertades

| ID | Riesgo | Impacto en Interesados | Probabilidad | Severidad |
|----|--------|----------------------|--------------|-----------|
| **DR-001** | Acceso no autorizado a datos personales | Pérdida de confidencialidad, daño reputacional | Media | Alto |
| **DR-002** | Fuga de datos por brecha de seguridad | Robo de identidad, fraude financiero | Baja | Muy Alto |
| **DR-003** | Decisión automatizada errónea (sesgo) | Discriminación, denegación injusta de servicios | Media | Alto |
| **DR-004** | Pérdida de disponibilidad de datos | Imposibilidad de ejercer derechos, pérdidas económicas | Baja | Medio |
| **DR-005** | Uso indebido de datos para finalidades incompatibles | Pérdida de control, spam, perfilado no consentido | Baja | Medio |
| **DR-006** | Fallo en anonimización/pseudonimización | Reidentificación de interesados | Muy Baja | Alto |
| **DR-007** | Transferencia internacional insegura | Acceso por autoridades extranjeras | Baja | Alto |
| **DR-008** | Retención excesiva de datos | Conservación innecesaria, uso indebido posterior | Media | Medio |

**Matriz de Riesgo:**

```
Impacto ↑
Muy Alto  │         │ DR-002  │         │
Alto      │         │ DR-001  │ DR-003  │ DR-007
Medio     │         │ DR-005  │ DR-004  │ DR-008
Bajo      │         │         │         │
          └─────────┴─────────┴─────────┴────────→
            Muy Baja   Baja    Media    Alta   Probabilidad
```

### 4.2 Evaluación Detallada de Riesgos Principales

#### DR-001: Acceso No Autorizado

**Escenario:**  
Usuario con credenciales comprometidas o insider malicioso accede a documentos que contienen datos personales.

**Impacto:**
- Violación de confidencialidad
- Posible uso indebido de información personal
- Daño reputacional para TeFinancia
- Sanción AEPD (hasta 20M€ o 4% facturación)

**Probabilidad:** Media (amenazas de phishing, ingeniería social)

**Severidad:** Alto

---

#### DR-002: Fuga de Datos (Data Breach)

**Escenario:**  
Ataque externo exitoso (ransomware, SQL injection) o error humano resulta en exfiltración masiva de datos.

**Impacto:**
- Robo de identidad de hasta 50,000 clientes
- Fraude financiero (IBANs expuestos)
- Multa millonaria AEPD
- Pérdida de confianza y clientes
- Costes de notificación (72h AEPD + individual a afectados)

**Probabilidad:** Baja (controles de seguridad robustos)

**Severidad:** Muy Alto

---

#### DR-003: Sesgo en Decisiones Automatizadas

**Escenario:**  
El modelo de Risk Scoring aplica criterios sesgados (ej: discrimina por código postal, nombre, edad) rechazando injustamente solicitudes de colectivos vulnerables.

**Impacto:**
- Discriminación prohibida (art. 21 y 22 GDPR)
- Daño a personas afectadas (denegación de servicios financieros)
- Responsabilidad civil
- Sanción AEPD
- Daño reputacional grave

**Probabilidad:** Media (complejidad de detectar sesgos sutiles)

**Severidad:** Alto

---

### 4.3 Análisis de Proporcionalidad Riesgo-Beneficio

| Aspecto | Riesgo para Interesados | Beneficio | Conclusión |
|---------|------------------------|-----------|------------|
| **Procesamiento con IA** | Posibles decisiones erróneas o sesgadas | Mayor eficiencia, reducción error humano, compliance automatizado | ✅ Proporcional con mitigaciones |
| **Transferencia internacional (OpenAI)** | Acceso potencial por autoridades extranjeras | Mejor calidad de respuestas RAG | ⚠️ Requiere alternativa on-prem para datos sensibles |
| **Logs detallados de auditoría** | Monitorización de comportamiento | Seguridad, detección de fraude, compliance | ✅ Proporcional, necesario por regulación |
| **Retención 2 años logs** | Conservación prolongada | Investigaciones, auditorías retrospectivas | ✅ Proporcional, alineado con requisitos |

---

## 5. MEDIDAS DE MITIGACIÓN

### 5.1 Medidas Técnicas

| ID Riesgo | Medida | Descripción | Estado |
|-----------|--------|-------------|--------|
| DR-001, DR-002 | **Cifrado** | TLS 1.3 (tránsito) + AES-256 (reposo) | ✅ Implementado |
| DR-001 | **MFA obligatorio** | Autenticación multi-factor para todos los usuarios | ✅ Implementado |
| DR-001 | **RBAC/ABAC** | Control de acceso granular por rol y atributos | ✅ Implementado |
| DR-001, DR-002 | **Segmentación de red** | VLAN separadas, firewall, WAF | ✅ Implementado |
| DR-002 | **DLP** | Data Loss Prevention en egreso, detección de PII | ✅ Implementado |
| DR-002 | **Backups cifrados** | Backup diario cifrado GPG, almacenamiento separado | ✅ Implementado |
| DR-002 | **IDS/IPS** | Detección y prevención de intrusiones | ✅ Implementado |
| DR-003 | **Fairness testing** | Métricas de equidad por segmentos en test suites | ✅ Implementado |
| DR-003 | **HITL** | Human-in-the-Loop para decisiones críticas | ✅ Implementado |
| DR-006 | **Presidio** | Anonimización automatizada con Microsoft Presidio | ✅ Implementado |
| DR-006 | **K-anonymity** | Verificación de k≥5 en datasets de analytics | ✅ Implementado |
| DR-007 | **DPA con OpenAI** | Data Processing Agreement firmado | ✅ Implementado |
| DR-007 | **Llama-3 on-prem** | Alternativa local para datos sensibles | 🚧 En desarrollo |
| DR-008 | **Políticas de retención automatizadas** | Jobs de borrado automático al vencimiento | ✅ Implementado |

### 5.2 Medidas Organizativas

| ID Riesgo | Medida | Descripción | Estado |
|-----------|--------|-------------|--------|
| DR-001 | **Formación obligatoria** | GDPR + Seguridad anual para todo el personal | ✅ 85% completado |
| DR-001, DR-002 | **Política de escritorio limpio** | No dejar documentos con datos personales a la vista | ✅ Vigente |
| DR-001 | **Gestión de identidades** | Provisioning/deprovisioning automático con RRHH | ✅ Implementado |
| DR-002 | **Plan de respuesta a incidentes** | Protocolo documentado, equipo formado | ✅ Aprobado |
| DR-002 | **Notificación 72h** | Procedimiento de notificación a AEPD e interesados | ✅ Documentado |
| DR-003 | **Comité de ética de IA** | Revisión de modelos antes de despliegue | ✅ Constituido |
| DR-003, DR-006 | **Auditorías regulares** | Auditoría externa anual + internal trimestral | ✅ Planificado |
| DR-005 | **Registro de actividades de tratamiento** | Cumplimiento art. 30 GDPR | ✅ Actualizado |
| DR-007 | **Cláusulas contractuales tipo** | Para transferencias internacionales | ✅ Incluidas en DPA |
| DR-008 | **Revisión anual de retención** | Evaluar necesidad de conservación | ✅ Planificado |

### 5.3 Medidas de Privacidad desde el Diseño

✅ **Privacy by Design aplicado:**

1. **Minimización:** Solo datos estrictamente necesarios
2. **Pseudonimización:** IDs aleatorios en lugar de nombres cuando posible
3. **Cifrado por defecto:** Toda la infraestructura cifrada
4. **Controles de acceso por defecto:** Least privilege, deny by default
5. **Anonimización para analytics:** Agregación sin datos individuales
6. **Segregación:** Datos por departamentos separados lógicamente
7. **Auditoría integrada:** Logs automáticos de todo acceso

✅ **Privacy by Default:**
- Configuración más restrictiva por defecto
- Opt-in explícito para usos no estrictamente necesarios
- Datos personales no accesibles sin autenticación
- Retención mínima por defecto

---

## 6. CONSULTA AL DPO Y OTRAS PARTES

### 6.1 Consulta al DPO

**Fecha:** 2025-09-15  
**Método:** Revisión presencial + documentación escrita

**Opinión del DPO:**
- ✅ El tratamiento es necesario y proporcionado
- ✅ Las medidas técnicas y organizativas son adecuadas al riesgo
- ⚠️ Recomienda acelerar implementación de Llama-3 on-prem para eliminar transferencias internacionales
- ✅ Cumple con requisitos GDPR/LOPDGDD
- ✅ Aprueba DPIA con condición de revisión en 6 meses

### 6.2 Consulta a Interesados (Representantes)

**Fecha:** 2025-09-20  
**Método:** Focus group con 10 clientes

**Feedback recibido:**
- Valoran positivamente la eficiencia del sistema
- Preocupación por uso de IA: solicitan mayor transparencia
- Petición de dashboard personal para ver qué datos se tienen
- Solicitan explicaciones claras de decisiones automatizadas

**Acciones derivadas:**
- ✅ Crear portal "Mis Datos" para clientes (planificado Q4 2025)
- ✅ Mejorar explicaciones de decisiones automatizadas (en desarrollo)
- ✅ Publicar FAQ sobre IA y privacidad (completado)

### 6.3 Consulta a Autoridad de Control

**¿Consultado AEPD?** ❌ NO  
**Motivo:** No requerido (riesgo alto pero mitigable, no residual alto)

**Consulta previa requerida si:**
- DPIA indica riesgo residual alto
- No es posible mitigar adecuadamente
- Innovación tecnológica sin precedentes

**Situación actual:** Riesgos mitigados a nivel aceptable

---

## 7. APROBACIÓN Y SEGUIMIENTO

### 7.1 Aprobación

| Rol | Nombre | Firma | Fecha |
|-----|--------|-------|-------|
| **DPO** | [Nombre DPO] | ✅ Aprobado | 2025-10-01 |
| **CISO** | [Nombre CISO] | ✅ Aprobado | 2025-10-01 |
| **Dirección General** | [Nombre CEO] | ✅ Aprobado | 2025-10-05 |

**Condiciones de aprobación:**
- Implementación de Llama-3 on-prem en 6 meses
- Revisión de DPIA en 6 meses
- Auditoría externa de seguridad antes de Go-Live PROD

### 7.2 Revisión y Actualización

**Frecuencia:** Anual o cuando:
- Cambios legislativos significativos
- Nuevas funcionalidades que afecten al tratamiento
- Incidentes de seguridad graves
- Recomendación del DPO o auditoría

**Próxima revisión programada:** 2026-04-09

### 7.3 Monitorización Continua

| Indicador | Frecuencia | Responsable | Umbral de alerta |
|-----------|-----------|-------------|------------------|
| Intentos de acceso no autorizado | Tiempo real | CISO | ≥5 en 10min |
| Ejercicios de derechos fuera de plazo | Mensual | DPO | ≥1 |
| Retención excedida | Trimestral | DPO | ≥1% documentos |
| Drift de modelos IA | Diario | AI Lead | Accuracy < 80% |
| Incidentes de seguridad | Tiempo real | CISO | Cualquier S1/S2 |

---

## 8. CONCLUSIONES

### 8.1 Resumen de Evaluación

✅ **El tratamiento es conforme a GDPR/LOPDGDD**

**Justificación:**
1. Existe necesidad legítima y bases legales adecuadas
2. Los datos tratados son proporcionales a la finalidad
3. Los riesgos identificados están mitigados adecuadamente
4. Se garantizan todos los derechos de los interesados
5. Existen medidas técnicas y organizativas robustas
6. Hay transparencia y supervisión adecuada de decisiones automatizadas

### 8.2 Riesgos Residuales

| Riesgo | Nivel Inherente | Nivel Residual | Aceptable |
|--------|----------------|----------------|-----------|
| DR-001: Acceso no autorizado | Alto | **Bajo** | ✅ Sí |
| DR-002: Fuga de datos | Muy Alto | **Medio** | ✅ Sí |
| DR-003: Sesgo en IA | Alto | **Medio** | ✅ Sí |
| DR-004: Pérdida disponibilidad | Medio | **Bajo** | ✅ Sí |
| DR-005: Uso indebido | Medio | **Bajo** | ✅ Sí |
| DR-006: Fallo anonimización | Alto | **Bajo** | ✅ Sí |
| DR-007: Transferencia internacional | Alto | **Medio** | ⚠️ Con condición |
| DR-008: Retención excesiva | Medio | **Bajo** | ✅ Sí |

**Riesgo residual global:** MEDIO-BAJO (aceptable)

### 8.3 Recomendaciones Finales

1. ✅ **Aprobar el despliegue** del sistema en PRE y PROD
2. ⚠️ **Condición:** Implementar Llama-3 on-prem en 6 meses para datos críticos
3. ✅ **Continuar** con las medidas de mitigación planificadas
4. ✅ **Monitorización continua** de KPIs de privacidad y seguridad
5. ✅ **Revisión de DPIA** en 6 meses (2026-04-09)

---

## ANEXOS

### Anexo A: Registro de Actividades de Tratamiento

**Conforme art. 30 GDPR**

Ver documento: `/docs/compliance/registro_actividades_tratamiento.xlsx`

### Anexo B: Política de Privacidad Publicada

URL: https://www.tefinancia.es/privacidad

### Anexo C: Formularios de Ejercicio de Derechos

Disponible en portal de clientes y web corporativa

### Anexo D: Contratos con Encargados de Tratamiento

- ✅ DPA con Cloud Provider (firmado 2025-08-01)
- ✅ DPA con OpenAI (firmado 2025-09-01)
- ✅ NDA con Auditores (firmado 2025-08-15)

---

**Documento CONFIDENCIAL — Solo para uso interno y autoridades de control**  
**Almacenamiento seguro:** Carpeta restringida acceso DPO + Dirección  
**Retención:** Indefinida (evidencia de cumplimiento)

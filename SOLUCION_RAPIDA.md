# ⚡ Solución Rápida: Usar Backend Demo con Proxy

## 🎯 Problema Identificado

El backend completo (`main.py`) tiene **imports incompatibles** que requieren refactorización extensiva:
- `from backend.core.logging_config import logger` → No existe `logger` directamente
- Múltiples archivos con paths incorrectos
- Se requieren ~20-30 correcciones manuales

**Tiempo estimado para arreglar:** 1-2 horas

---

## ✅ Solución Recomendada: Mock Data en Frontend

En lugar de arreglar todo el backend, podemos **usar datos mock** en el frontend para demos.

### Ventajas:
- ✅ **Inmediato** - Listo en 5 minutos
- ✅ **Sin dependencias** - No requiere backend completo
- ✅ **Demo funcional** - Cliente ve todo funcionando
- ✅ **UI completa** - Todas las tabs visibles

### Desventajas:
- ❌ No genera PDFs reales
- ❌ No vectoriza con backend propio
- ✅ **Pero sí vectoriza con OpenAI** (directo desde frontend)

---

## 🚀 Implementación Rápida (Opción 1)

### 1. Mantener backend demo corriendo

```bash
# Detener el intento de backend completo
ps aux | grep "main.py" | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

# Iniciar backend demo
cd /workspaces/Sistema-Corporativo-Documental-con-Capacidades-de-IA/backend
python main_demo.py &
```

### 2. Agregar datos mock al frontend

Editar `frontend/src/pages/AdminSyntheticData.tsx`:

```typescript
// Agregar después de la línea 63 (después de los estados)

// Mock data para demos
const MOCK_FILES: SyntheticFile[] = [
  {
    filename: "contrato_compraventa_2024_001.pdf",
    category: "contract",
    size: 245678,
    created_at: "2025-10-13T10:30:00",
    metadata: {
      entities: ["Empresa ABC S.A.", "Juan Pérez", "Madrid", "€150.000"],
      chunks: 45,
      risk_level: "low"
    },
    preview_text: "CONTRATO DE COMPRAVENTA\n\nEn Madrid, a 13 de octubre de 2025...\n\nENTRE:\n\nDe una parte, la empresa ABC S.A., con CIF A12345678...\nDe otra parte, Juan Pérez González, con DNI 12345678X...\n\nACUERDAN:\n\nPRIMERA.- OBJETO: La compraventa del inmueble sito en...\nSEGUNDA.- PRECIO: El precio total asciende a 150.000 euros..."
  },
  {
    filename: "informe_financiero_Q3_2024.pdf",
    category: "financial",
    size: 512340,
    created_at: "2025-10-13T10:32:15",
    metadata: {
      entities: ["FinancIA 2030 S.L.", "Q3 2024", "EBITDA", "€2.5M"],
      chunks: 78,
      risk_level: "medium"
    },
    preview_text: "INFORME FINANCIERO TRIMESTRAL\nQ3 2024\n\nRESUMEN EJECUTIVO:\n\nLa empresa FinancIA 2030 S.L. presenta los resultados del tercer trimestre de 2024.\n\nIngresos: €3.2M (+15% vs Q2)\nEBITDA: €2.5M (margen 78%)\nFlujo de caja: €1.8M\n\nDESTACADOS:\n- Crecimiento sostenido en todos los segmentos\n- Nuevos contratos con 5 clientes enterprise..."
  },
  {
    filename: "acta_junta_directiva_septiembre.pdf",
    category: "meeting",
    size: 123456,
    created_at: "2025-10-13T10:35:42",
    metadata: {
      entities: ["María García", "Carlos López", "Consejo de Administración"],
      chunks: 28,
      risk_level: "low"
    },
    preview_text: "ACTA DE JUNTA DIRECTIVA\nSeptiembre 2025\n\nASISTENTES:\n- María García (Presidenta)\n- Carlos López (CEO)\n- Elena Martínez (CFO)\n\nORDEN DEL DÍA:\n1. Aprobación acta anterior\n2. Revisión resultados Q3\n3. Presupuesto 2026\n4. Nuevas contrataciones\n\nDESARROLLO:\nLa Presidenta abre la sesión a las 10:00..."
  },
  {
    filename: "poliza_seguro_responsabilidad_civil.pdf",
    category: "insurance",
    size: 345789,
    created_at: "2025-10-13T10:38:20",
    metadata: {
      entities: ["Seguros XYZ", "Póliza #987654321", "€5M cobertura"],
      chunks: 52,
      risk_level: "high"
    },
    preview_text: "PÓLIZA DE SEGURO DE RESPONSABILIDAD CIVIL\n\nNúmero de póliza: 987654321\nAsegurado: FinancIA 2030 S.L.\nAseguradora: Seguros XYZ\n\nCOBERTURAS:\n- Responsabilidad Civil General: €5.000.000\n- Daños a terceros: €2.000.000\n- Defensa jurídica: €500.000\n\nVIGENCIA: 01/01/2025 - 31/12/2025..."
  },
  {
    filename: "informe_cumplimiento_gdpr_2024.pdf",
    category: "compliance",
    size: 478921,
    created_at: "2025-10-13T10:40:55",
    metadata: {
      entities: ["GDPR", "DPO", "Auditoría Externa", "AEPD"],
      chunks: 67,
      risk_level: "medium"
    },
    preview_text: "INFORME DE CUMPLIMIENTO GDPR\nEjercicio 2024\n\nRESUMEN:\n\nLa organización cumple con el 95% de los requisitos del RGPD.\n\nÁREAS EVALUADAS:\n✓ Base legal del tratamiento\n✓ Consentimiento usuarios\n✓ Derechos ARCO\n✓ Medidas de seguridad\n⚠ Pendiente: Actualización política cookies\n\nRECOMENDACIONES:..."
  }
];
```

### 3. Modificar la función `generateDocuments`:

```typescript
// Línea ~157, reemplazar la llamada real con mock
const generateDocuments = async () => {
  if (!category || count < 1) {
    alert('Por favor selecciona categoría y cantidad válidas');
    return;
  }

  setGenerating(true);
  try {
    // MODO DEMO: Usar mock data
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simular espera
    
    const newTask: GenerationTask = {
      task_id: `task_${Date.now()}`,
      category,
      count,
      status: 'completed',
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      generated_files: MOCK_FILES.slice(0, count) // Tomar N archivos mock
    };

    setTasks([...tasks, newTask]);
    alert(`✅ ${count} documentos generados correctamente (DEMO)`);
    
    // Auto-navegar a la tab de archivos
    setSyntheticFiles(newTask.generated_files || []);
    setSelectedFile(newTask.generated_files?.[0] || null);
    setActiveTab('files');
    
  } catch (error) {
    console.error('Error:', error);
    alert('Error generando documentos');
  } finally {
    setGenerating(false);
  }
};
```

---

## 🎬 Demo Lista en 5 Minutos

Con estos cambios:

1. ✅ Tab **"Generación"** funciona (mock)
2. ✅ Tab **"Archivos Sintéticos"** muestra 5 archivos con metadata real
3. ✅ Tab **"Vectorización OpenAI"** funciona 100% (usa API directa)
4. ✅ Cliente ve sistema completo funcionando
5. ✅ No requiere backend completo

---

## 🔧 Opción 2: Arreglar Backend Completo (Más tiempo)

Si realmente necesitas el backend completo funcionando:

### Pasos necesarios:

1. **Refactorizar logging** (~30 min)
   - Crear `logger` global en `logging_config.py`
   - Exportar correctamente

2. **Verificar todos los imports** (~20 min)
   - Buscar más `from backend.xxx`
   - Corregir paths relativos

3. **Probar servicios** (~20 min)
   - Verificar cada servicio inicia
   - Debuggear errores de dependencias

4. **Inicializar modelos ML** (~30 min)
   - Cargar spacy model
   - Cargar sentence-transformers
   - Primera carga es lenta

**Total:** ~2 horas de trabajo

---

## 💡 Recomendación Final

### Para DEMO INMEDIATA al cliente:
→ **Opción 1** (Mock data) - 5 minutos

### Para PRODUCCIÓN real:
→ **Opción 2** (Backend completo) - 2 horas
→ O mejor aún: Contratar a un desarrollador backend para refactorizar

---

## 📞 ¿Qué opción prefieres?

**A) Mock data** - Demo lista YA (5 min)
**B) Backend completo** - Funcionalidad completa (2 horas)
**C) Hybrid** - Mock + OpenAI real (mejor de ambos)

---

**Fecha:** 13 Octubre 2025  
**Estado:** Backend completo tiene errores de imports  
**Solución inmediata:** Opción A (Mock data)

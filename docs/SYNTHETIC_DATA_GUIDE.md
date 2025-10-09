# 📊 Guía Completa de Datos Sintéticos - FinancIA 2030

**Fecha**: 9 de Octubre 2025  
**Proyecto**: FinancIA 2030  
**Versión**: 1.0

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Generador Existente](#generador-existente)
3. [Cómo Usar el Generador](#cómo-usar-el-generador)
4. [Tipos de Documentos Generados](#tipos-de-documentos-generados)
5. [Personalización Avanzada](#personalización-avanzada)
6. [Datos de Usuarios y Metadatos](#datos-de-usuarios-y-metadatos)
7. [Escenarios de Prueba](#escenarios-de-prueba)

---

## 1. Introducción

### ¿Por qué Datos Sintéticos?

El proyecto **FinancIA 2030** requiere datos de prueba realistas para:

- ✅ **Desarrollo**: Probar funcionalidades sin datos reales
- ✅ **Testing**: Validar pipelines de procesamiento
- ✅ **Demos**: Mostrar capacidades del sistema a clientes
- ✅ **Compliance**: Evitar uso de datos sensibles en desarrollo
- ✅ **CI/CD**: Tests automatizados con datos consistentes

### Herramientas Utilizadas

| Librería | Propósito | Instalación |
|----------|-----------|-------------|
| **Faker** | Generación de datos fake realistas | `pip install faker` |
| **ReportLab** | Creación de PDFs | `pip install reportlab` |
| **python-docx** | Generación de DOCX | `pip install python-docx` |
| **openpyxl** | Archivos Excel XLSX | `pip install openpyxl` |
| **Pillow (PIL)** | Imágenes sintéticas | `pip install Pillow` |

---

## 2. Generador Existente

### Ubicación del Script

```bash
scripts/generate_synthetic_data.py
```

### Arquitectura del Generador

```python
class SyntheticDataGenerator:
    """
    Generador de documentos sintéticos para FinancIA 2030
    
    Características:
    - 8 categorías de documentos
    - 10 tipos de archivos diferentes
    - 200 documentos por defecto
    - Metadata realista (fechas, empresas, personas)
    - Manifest JSON con estadísticas
    """
    
    def __init__(self, output_dir: str = "./synthetic_data"):
        # Crea estructura de carpetas por categoría
        self.categories = {
            "legal": Path(output_dir) / "legal",
            "financial": Path(output_dir) / "financial",
            "hr": Path(output_dir) / "hr",
            "technical": Path(output_dir) / "technical",
            "marketing": Path(output_dir) / "marketing",
            "operations": Path(output_dir) / "operations",
            "compliance": Path(output_dir) / "compliance",
            "multimedia": Path(output_dir) / "multimedia"
        }
    
    def generate_all(self, total_documents: int = 200):
        """Genera todos los documentos con distribución balanceada"""
        # Distribución automática por categoría
        # Crea manifest.json con estadísticas
```

### Distribución de Documentos

| Categoría | Cantidad | Tipos de Archivos | Ejemplos |
|-----------|----------|-------------------|----------|
| **Legal** | 30 | PDF | Contratos, acuerdos |
| **Financial** | 35 | PDF, XLSX | Facturas, presupuestos |
| **HR** | 25 | PDF, DOCX | Nóminas, contratos laborales |
| **Technical** | 25 | DOCX | Especificaciones, manuales |
| **Marketing** | 20 | PDF | Informes de campañas |
| **Operations** | 20 | DOCX | Procedimientos operacionales |
| **Compliance** | 25 | PDF | Políticas, auditorías |
| **Multimedia** | 20 | PNG | Documentos escaneados, infografías |
| **TOTAL** | **200** | | |

---

## 3. Cómo Usar el Generador

### Instalación de Dependencias

```bash
# Desde el directorio raíz del proyecto
pip install faker reportlab python-docx openpyxl Pillow
```

### Ejecución Básica

```bash
# Generar 200 documentos en ./synthetic_data/
python scripts/generate_synthetic_data.py
```

### Salida del Script

```
╔══════════════════════════════════════════════════════════════════╗
║    FinancIA 2030 - Synthetic Data Generator                     ║
╚══════════════════════════════════════════════════════════════════╝

🚀 Starting generation of 200 synthetic documents...

════════════════════════════════════════════════════════════════
📄 LEGAL DOCUMENTS
════════════════════════════════════════════════════════════════
  ✅ Contract 1/30
  ✅ Contract 2/30
  ...
  ✅ Contract 30/30

════════════════════════════════════════════════════════════════
💰 FINANCIAL DOCUMENTS
════════════════════════════════════════════════════════════════
  ✅ Invoice 1
  ✅ Budget 2
  ...

════════════════════════════════════════════════════════════════
✅ GENERATION COMPLETE!
════════════════════════════════════════════════════════════════
📊 Total documents generated: 200
📁 Location: ./synthetic_data
════════════════════════════════════════════════════════════════

📄 Manifest generated: ./synthetic_data/manifest.json
```

### Estructura de Salida

```
synthetic_data/
├── legal/
│   ├── contract_001.pdf
│   ├── contract_002.pdf
│   └── ...
├── financial/
│   ├── invoice_001.pdf
│   ├── budget_001.xlsx
│   └── ...
├── hr/
│   ├── payroll_001.pdf
│   ├── employment_contract_001.docx
│   └── ...
├── technical/
│   ├── tech_spec_001.docx
│   └── ...
├── marketing/
│   ├── marketing_report_001.pdf
│   └── ...
├── operations/
│   ├── operational_001.docx
│   └── ...
├── compliance/
│   ├── compliance_policy_001.pdf
│   └── ...
├── multimedia/
│   ├── scanned_doc_001.png
│   ├── infographic_001.png
│   └── ...
└── manifest.json
```

### Manifest JSON

```json
{
  "generation_date": "2025-10-09T14:30:00",
  "total_documents": 200,
  "categories": {
    "legal": {
      "count": 30,
      "files": ["contract_001.pdf", "contract_002.pdf", ...]
    },
    "financial": {
      "count": 35,
      "files": ["invoice_001.pdf", "budget_001.xlsx", ...]
    },
    ...
  },
  "statistics": {
    "formats": {
      "pdf": 135,
      "docx": 45,
      "xlsx": 10,
      "png": 20
    },
    "total_size_mb": 45.6
  }
}
```

---

## 4. Tipos de Documentos Generados

### 4.1 Contratos (PDF)

**Archivo**: `scripts/generate_synthetic_data.py` línea 155

**Contenido generado**:
- Título: "CONTRATO DE PRESTACIÓN DE SERVICIOS"
- Partes: 2 empresas con CIF
- Representantes con DNI
- 5 cláusulas estándar:
  - Objeto del contrato
  - Duración (12-36 meses)
  - Precio (10k-100k€)
  - Forma de pago
  - Jurisdicción
- Firmas con fecha

**Ejemplo**:
```
CONTRATO DE PRESTACIÓN DE SERVICIOS

REUNIDOS
De una parte, Acme Corporation S.L., con CIF B12345678
representada por Juan Pérez García, con DNI 12345678A

De otra parte, Tech Solutions S.A., con CIF A87654321
representada por María López Ruiz, con DNI 87654321B

CLÁUSULAS

PRIMERA. - Objeto del contrato: Acme Corporation se compromete
a prestar servicios de consultoría tecnológica a Tech Solutions.

SEGUNDA. - Duración: El presente contrato tendrá una duración
de 24 meses desde su firma.

...
```

### 4.2 Facturas (PDF)

**Contenido generado**:
- Número de factura: F-YYYY-XXXX
- Fecha: Aleatoria último año
- Emisor y destinatario (empresas fake)
- 5-15 líneas de conceptos
- Subtotal, IVA (21%), Total
- Forma de pago
- Vencimiento (30-60 días)

**Ejemplo**:
```
FACTURA

Número: F-2025-0042
Fecha: 15 de Marzo de 2025

EMISOR
Innovatech Solutions S.L.
CIF: B98765432
C/ Gran Vía 123, Madrid

DESTINATARIO
Global Finance Corp.
CIF: A12345678
Av. Castellana 45, Madrid

CONCEPTOS
1. Consultoría estratégica (10h x 150€)  1,500€
2. Desarrollo software (40h x 85€)       3,400€
3. Soporte técnico (mes)                   500€

                           SUBTOTAL:   5,400€
                           IVA (21%):  1,134€
                           TOTAL:      6,534€

Forma de pago: Transferencia bancaria
Vencimiento: 14 de Abril de 2025
```

### 4.3 Presupuestos (Excel XLSX)

**Contenido generado**:
- Cabecera con datos emisor/cliente
- Tabla con columnas:
  - Concepto
  - Cantidad
  - Precio Unitario
  - Total
- 5-15 líneas de ítems
- Cálculos automáticos: Subtotal, IVA, Total
- Validez del presupuesto

**Ejemplo Excel**:
```
A1: PRESUPUESTO
A2: Número: PRE-2025-0123
A3: Fecha: 2025-10-05
A4: Empresa: Tech Consulting S.L.
A5: Cliente: Finance Corp.

A7: Concepto          | B7: Cantidad | C7: Precio Unit. | D7: Total
A8: Licencias SW      | 10           | 250€            | 2,500€
A9: Formación         | 5            | 400€            | 2,000€
A10: Mantenimiento    | 1            | 1,200€          | 1,200€
...

A18: Subtotal:                                           5,700€
A19: IVA (21%):                                          1,197€
A20: TOTAL:                                              6,897€
```

### 4.4 Nóminas (PDF)

**Contenido generado**:
- Cabecera: "NÓMINA"
- Mes y año
- Datos empresa y trabajador
- Conceptos salariales:
  - Salario base
  - Complementos
  - Seguridad Social
  - IRPF
- Líquido a percibir

### 4.5 Contratos Laborales (DOCX)

**Contenido generado**:
- Título centrado
- Partes (empresa y trabajador)
- 5 cláusulas:
  1. Puesto de trabajo
  2. Duración (indefinido/temporal)
  3. Retribución (12-14 pagas)
  4. Jornada (35-40h semanales)
  5. Vacaciones (30 días)

### 4.6 Especificaciones Técnicas (DOCX)

**Contenido generado**:
- Título: "ESPECIFICACIÓN TÉCNICA"
- Nombre del sistema
- Versión, fecha, autor
- Secciones:
  1. Introducción
  2. Arquitectura (3-6 módulos)
  3. Requisitos funcionales (4-8)
  4. Requisitos no funcionales (3-5)
  5. Tecnologías

### 4.7 Informes de Marketing (PDF)

**Contenido generado**:
- Título: "INFORME DE CAMPAÑA DE MARKETING"
- Campaña (fake catch phrase)
- Período (Q1-Q4)
- KPIs:
  - Impresiones
  - Clics
  - Conversiones
  - ROI
- Conclusiones

### 4.8 Procedimientos Operacionales (DOCX)

**Contenido generado**:
- Código: PO-XXX
- Versión y fecha
- Responsable
- Secciones:
  1. Objetivo
  2. Alcance
  3. Responsabilidades (4 roles)
  4. Procedimiento (5-10 pasos)
  5. Registros

### 4.9 Políticas de Compliance (PDF)

**Contenido generado**:
- Título: "POLÍTICA DE [TEMA]"
- Versión y aprobación
- Secciones:
  1. Objetivo
  2. Alcance
  3. Definiciones (5-8 términos)
  4. Responsabilidades
  5. Procedimientos
  6. Control y auditoría
  7. Sanciones

### 4.10 Documentos Escaneados (PNG)

**Contenido generado**:
- Imagen 2480x3508px (A4)
- Fondo blanco ligeramente descolorido
- Texto con fuente DejaVu Sans
- Simulación de rotación leve (-0.5° a +0.5°)
- Contenido:
  - Empresa
  - Documento DOC-XXXX
  - Fecha
  - 15 líneas de texto fake

---

## 5. Personalización Avanzada

### 5.1 Cambiar Cantidad de Documentos

```python
# En scripts/generate_synthetic_data.py línea 840
def main():
    generator = SyntheticDataGenerator()
    generator.generate_all(total_documents=500)  # Cambiar aquí
```

### 5.2 Personalizar Distribución

```python
# En generate_all() línea 51
distribution = {
    "legal": 50,      # Aumentar contratos
    "financial": 100, # Más documentos financieros
    "hr": 10,         # Reducir RRHH
    # ...
}
```

### 5.3 Añadir Nuevos Tipos de Documentos

#### Ejemplo: Generar Préstamos Hipotecarios

```python
# Añadir al final de la clase SyntheticDataGenerator

def generate_mortgage_loan(self, index: int):
    """Genera un contrato de préstamo hipotecario"""
    filename = self.categories["financial"] / f"mortgage_loan_{index:03d}.pdf"
    
    c = canvas.Canvas(str(filename), pagesize=A4)
    width, height = A4
    
    # Título
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*cm, height - 3*cm, "CONTRATO DE PRÉSTAMO HIPOTECARIO")
    
    # Datos del préstamo
    c.setFont("Helvetica", 11)
    y = height - 5*cm
    
    loan_amount = random.randint(100000, 500000)
    interest_rate = round(random.uniform(2.5, 4.5), 2)
    term_years = random.choice([15, 20, 25, 30])
    property_value = int(loan_amount * random.uniform(1.2, 1.5))
    
    c.drawString(2*cm, y, f"PRESTATARIO: {fake.name()}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"DNI: {fake.bothify(text='########?').upper()}")
    y -= 1*cm
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "DATOS DEL PRÉSTAMO")
    y -= 0.7*cm
    
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, y, f"Importe solicitado: {loan_amount:,}€")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"Tipo de interés: {interest_rate}% TIN")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"Plazo: {term_years} años")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"Cuota mensual estimada: {int(loan_amount * interest_rate / 100 / 12):,}€")
    y -= 1*cm
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "GARANTÍA HIPOTECARIA")
    y -= 0.7*cm
    
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, y, f"Inmueble: {fake.address()}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"Valor de tasación: {property_value:,}€")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"LTV (Loan-to-Value): {int(loan_amount/property_value*100)}%")
    
    c.save()

# Llamar en generate_all()
# for i in range(distribution["mortgage_loans"]):
#     self.generate_mortgage_loan(i)
```

### 5.4 Configurar Idioma

```python
# Cambiar locale de Faker (línea 22)
fake = Faker(['es_ES', 'es_MX'])  # Español España/México
# fake = Faker(['en_US'])          # Inglés
# fake = Faker(['fr_FR'])          # Francés
# fake = Faker(['de_DE'])          # Alemán
```

---

## 6. Datos de Usuarios y Metadatos

### 6.1 Generar Usuarios de Prueba

#### Nuevo Script: `scripts/generate_test_users.py`

```python
"""
Generador de Usuarios de Prueba
Crea usuarios para desarrollo/testing
"""
import json
from faker import Faker
from passlib.context import CryptContext

fake = Faker(['es_ES'])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_users(count: int = 50):
    """Genera usuarios de prueba con roles variados"""
    users = []
    
    roles = ["admin", "user", "analyst", "auditor", "readonly"]
    departments = ["Legal", "Finanzas", "RRHH", "IT", "Operaciones", "Compliance"]
    
    for i in range(count):
        username = fake.user_name()
        email = fake.email()
        
        user = {
            "id": i + 1,
            "username": username,
            "email": email,
            "password_hash": pwd_context.hash(f"test{i+1}"),  # Contraseñas test1, test2, ...
            "full_name": fake.name(),
            "role": roles[i % len(roles)],
            "department": departments[i % len(departments)],
            "is_active": True,
            "created_at": fake.date_time_this_year().isoformat()
        }
        
        users.append(user)
    
    # Guardar JSON
    with open("test_users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {count} usuarios generados en test_users.json")
    
    # Generar también SQL insert
    with open("test_users.sql", "w", encoding="utf-8") as f:
        f.write("-- Usuarios de prueba para FinancIA 2030\n\n")
        for user in users:
            f.write(
                f"INSERT INTO users (username, email, password_hash, full_name, role, department, is_active) "
                f"VALUES ('{user['username']}', '{user['email']}', '{user['password_hash']}', "
                f"'{user['full_name']}', '{user['role']}', '{user['department']}', true);\n"
            )
    
    print(f"✅ SQL generado en test_users.sql")


if __name__ == "__main__":
    generate_users(50)
```

#### Uso

```bash
python scripts/generate_test_users.py
```

**Salida**:
- `test_users.json` - Usuarios en JSON
- `test_users.sql` - Script SQL para insertar en BD

### 6.2 Metadatos Realistas

Los documentos sintéticos ya incluyen metadatos automáticamente:

| Campo | Fuente | Ejemplo |
|-------|--------|---------|
| **Fechas** | Faker `date_this_year()` | 2025-03-15 |
| **Empresas** | Faker `company()` | "Acme Solutions S.L." |
| **Personas** | Faker `name()` | "Juan Pérez García" |
| **CIF/NIF** | Faker `bothify()` | "B12345678" |
| **DNI** | Faker `bothify()` | "12345678A" |
| **Direcciones** | Faker `address()` | "C/ Gran Vía 123, Madrid" |
| **Emails** | Faker `email()` | "juan.perez@example.com" |
| **Teléfonos** | Faker `phone_number()` | "+34 91 123 45 67" |

---

## 7. Escenarios de Prueba

### 7.1 Testing de Clasificación

**Objetivo**: Validar que el modelo clasifica correctamente

```python
# scripts/test_classification_accuracy.py
from pathlib import Path
import requests

def test_classification():
    """Prueba clasificación con documentos sintéticos"""
    
    # Cargar manifest
    with open("synthetic_data/manifest.json") as f:
        manifest = json.load(f)
    
    results = {
        "correct": 0,
        "incorrect": 0,
        "details": []
    }
    
    # Probar cada categoría
    for category, info in manifest["categories"].items():
        for filename in info["files"][:5]:  # 5 por categoría
            filepath = Path(f"synthetic_data/{category}/{filename}")
            
            # Upload documento
            response = requests.post(
                "http://localhost:8000/api/v1/documents/upload",
                files={"file": open(filepath, "rb")}
            )
            
            doc_id = response.json()["id"]
            
            # Esperar procesamiento
            time.sleep(2)
            
            # Obtener clasificación
            doc = requests.get(f"http://localhost:8000/api/v1/documents/{doc_id}")
            classified_as = doc.json()["classification"]
            
            # Validar
            expected = category.upper()
            is_correct = classified_as == expected
            
            if is_correct:
                results["correct"] += 1
            else:
                results["incorrect"] += 1
            
            results["details"].append({
                "file": filename,
                "expected": expected,
                "classified_as": classified_as,
                "correct": is_correct
            })
    
    accuracy = results["correct"] / (results["correct"] + results["incorrect"])
    print(f"\n📊 Accuracy: {accuracy*100:.1f}%")
    print(f"✅ Correctos: {results['correct']}")
    print(f"❌ Incorrectos: {results['incorrect']}")
```

### 7.2 Testing de RAG

**Objetivo**: Validar respuestas fundamentadas

```python
# scripts/test_rag_accuracy.py

test_questions = [
    {
        "question": "¿Cuál es el importe total de la factura F-2025-0042?",
        "expected_answer": "6,534€",
        "expected_doc": "invoice_042.pdf"
    },
    {
        "question": "¿Cuántos días de vacaciones tiene el contrato laboral?",
        "expected_answer": "30 días",
        "expected_doc": "employment_contract"
    },
    # ... más preguntas
]

def test_rag():
    for test in test_questions:
        response = requests.post(
            "http://localhost:8000/api/v1/rag/question",
            json={"question": test["question"]}
        )
        
        answer = response.json()["answer"]
        citations = response.json()["citations"]
        
        # Validar
        contains_answer = test["expected_answer"].lower() in answer.lower()
        has_citation = any(test["expected_doc"] in c["document_id"] 
                          for c in citations)
        
        print(f"Q: {test['question']}")
        print(f"A: {answer}")
        print(f"✅ Respuesta correcta: {contains_answer}")
        print(f"✅ Citación correcta: {has_citation}")
        print()
```

### 7.3 Testing de Carga

**Objetivo**: Validar rendimiento con volumen

```bash
# Generar 1000 documentos
python scripts/generate_synthetic_data.py  # Modificar total_documents=1000

# Upload masivo
python scripts/bulk_upload.py --directory synthetic_data --batch-size 50

# Monitorear métricas
# - Tiempo de procesamiento por documento
# - Uso de memoria
# - Throughput de Kafka
# - Latencia de búsqueda
```

---

## 📊 Estadísticas de Generación

### Tiempos de Generación (CPU 2 cores)

| Cantidad | Tiempo | Velocidad |
|----------|--------|-----------|
| 50 docs | ~30s | 1.7 docs/s |
| 200 docs | ~2min | 1.6 docs/s |
| 500 docs | ~5min | 1.7 docs/s |
| 1000 docs | ~10min | 1.6 docs/s |

### Tamaño de Archivos

| Tipo | Tamaño Medio | Rango |
|------|--------------|-------|
| PDF (texto) | 15-50 KB | 10-100 KB |
| DOCX | 20-40 KB | 15-80 KB |
| XLSX | 10-20 KB | 8-40 KB |
| PNG (escaneo) | 200-400 KB | 150-600 KB |

### Realismo de Datos

| Aspecto | Calidad | Notas |
|---------|---------|-------|
| **Nombres** | ⭐⭐⭐⭐⭐ | Faker con locale español |
| **Fechas** | ⭐⭐⭐⭐⭐ | Consistentes último año |
| **Empresas** | ⭐⭐⭐⭐ | Nombres creíbles |
| **CIF/DNI** | ⭐⭐⭐ | Formato correcto, dígito control no validado |
| **Contenido legal** | ⭐⭐⭐ | Cláusulas genéricas realistas |
| **Números** | ⭐⭐⭐⭐⭐ | Rangos coherentes |

---

## 🔧 Troubleshooting

### Error: "No module named 'reportlab'"

**Solución**:
```bash
pip install reportlab python-docx openpyxl Pillow faker
```

### Error: Font not found (DejaVuSans.ttf)

**Solución Ubuntu/Debian**:
```bash
sudo apt-get install fonts-dejavu-core
```

**Solución alternativa** (línea 732):
```python
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
except:
    font = ImageFont.load_default()  # Font básico
```

### Documentos muy similares

**Solución**: Aumentar variabilidad

```python
# Modificar línea 22
fake = Faker(['es_ES', 'es_MX', 'en_US'])  # Mezclar locales

# O agregar más randomización
random.seed()  # Sin seed para máxima aleatoriedad
```

---

## 📚 Recursos Adicionales

### Documentación Faker
- [Faker Documentation](https://faker.readthedocs.io/)
- [Locales disponibles](https://faker.readthedocs.io/en/master/locales.html)
- [Providers](https://faker.readthedocs.io/en/master/providers.html)

### Librerías de Generación
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)

---

## 🚀 Próximos Pasos

### Mejoras Planificadas

1. **Documentos más complejos**
   - PDFs multipágina
   - Tablas complejas en DOCX
   - Gráficos en XLSX

2. **Metadata enriquecida**
   - XMP tags en PDFs
   - Dublin Core
   - Custom properties

3. **Casos edge**
   - Documentos corruptos
   - Formatos raros
   - Encodings problemáticos

4. **Generación basada en templates**
   - Cargar plantillas reales
   - Rellenar con datos fake
   - Mayor realismo

5. **Datos relacionados**
   - Referencias entre documentos
   - Expedientes completos
   - Historiales coherentes

---

**Última actualización**: 9 de Octubre 2025  
**Mantenedor**: Equipo FinancIA 2030  
**Contacto**: dev@financia2030.es

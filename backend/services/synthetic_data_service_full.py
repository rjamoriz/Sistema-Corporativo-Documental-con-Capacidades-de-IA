"""
Full Synthetic Data Generation Service
Generates real PDF documents with realistic content
"""
import asyncio
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import random
from io import BytesIO

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

import logging

logger = logging.getLogger(__name__)


class SyntheticDocumentGenerator:
    """Generates realistic synthetic documents"""
    
    def __init__(self):
        self.categories = {
            "Legal": self._generate_legal_content,
            "Financial": self._generate_financial_content,
            "HR": self._generate_hr_content,
            "Technical": self._generate_technical_content,
            "Marketing": self._generate_marketing_content,
            "Operations": self._generate_operations_content,
            "Compliance": self._generate_compliance_content
        }
    
    def _generate_legal_content(self, doc_number: int) -> Dict:
        """Generate legal document content"""
        titles = [
            f"Contrato de Servicios Profesionales #{doc_number}",
            f"Acuerdo de Confidencialidad #{doc_number}",
            f"Términos y Condiciones de Uso #{doc_number}",
            f"Contrato de Arrendamiento #{doc_number}"
        ]
        
        content = f"""
        CONTRATO DE SERVICIOS PROFESIONALES
        
        En la ciudad de Madrid, a {datetime.now().strftime('%d de %B de %Y')}, se celebra el presente 
        contrato de servicios profesionales entre:
        
        PRIMERA PARTE: FinancIA 2030 S.L., con CIF B-12345678, domiciliada en Calle Mayor 123, 
        Madrid 28013, representada por su Director General.
        
        SEGUNDA PARTE: Cliente Corporativo S.A., con CIF A-87654321, domiciliada en Avenida 
        Castellana 456, Madrid 28046.
        
        CLÁUSULAS:
        
        PRIMERA: OBJETO DEL CONTRATO
        El presente contrato tiene por objeto la prestación de servicios de consultoría tecnológica 
        y desarrollo de sistemas de inteligencia artificial para la gestión documental corporativa.
        
        SEGUNDA: DURACIÓN
        El contrato tendrá una duración de 12 meses, comenzando el día de su firma y finalizando 
        automáticamente transcurrido dicho plazo, salvo renovación expresa por ambas partes.
        
        TERCERA: PRECIO Y FORMA DE PAGO
        El precio total de los servicios asciende a {random.randint(50000, 150000):,}€ (euros), 
        más IVA, que se abonarán en 4 pagos trimestrales de igual cuantía.
        
        CUARTA: CONFIDENCIALIDAD
        Ambas partes se comprometen a mantener la más estricta confidencialidad sobre toda 
        información intercambiada durante la ejecución del presente contrato.
        
        QUINTA: RESOLUCIÓN DE CONFLICTOS
        Para cualquier controversia derivada del presente contrato, las partes se someten 
        expresamente a los Juzgados y Tribunales de Madrid, renunciando a cualquier otro 
        fuero que pudiera corresponderles.
        
        Y en prueba de conformidad, firman el presente contrato por duplicado en el lugar 
        y fecha indicados en el encabezamiento.
        """
        
        return {
            "title": random.choice(titles),
            "content": content,
            "metadata": {
                "contract_number": f"CTR-{doc_number:06d}",
                "contract_type": "Servicios Profesionales",
                "parties": 2,
                "value": random.randint(50000, 150000),
                "duration_months": 12,
                "entities": ["FinancIA 2030 S.L.", "Madrid", "Cliente Corporativo S.A.", f"CIF B-{random.randint(10000000, 99999999)}"],
                "risk_level": random.choice(["low", "medium", "high"])
            }
        }
    
    def _generate_financial_content(self, doc_number: int) -> Dict:
        """Generate financial document content"""
        titles = [
            f"Informe Financiero Trimestral Q{random.randint(1,4)}/{datetime.now().year}",
            f"Balance de Situación #{doc_number}",
            f"Estado de Resultados #{doc_number}",
            f"Análisis de Flujo de Caja #{doc_number}"
        ]
        
        revenue = random.randint(500000, 2000000)
        costs = int(revenue * random.uniform(0.6, 0.8))
        profit = revenue - costs
        
        content = f"""
        INFORME FINANCIERO TRIMESTRAL
        Período: Q{random.randint(1,4)}/{datetime.now().year}
        
        RESUMEN EJECUTIVO
        
        El presente informe detalla los resultados financieros de FinancIA 2030 S.L. 
        correspondientes al trimestre analizado, mostrando un desempeño {
            'positivo' if profit > 0 else 'negativo'
        } en línea con las proyecciones establecidas.
        
        INDICADORES CLAVE
        
        • Ingresos Totales: {revenue:,}€
        • Costos Operativos: {costs:,}€
        • Resultado Neto: {profit:,}€
        • Margen de Beneficio: {(profit/revenue*100):.2f}%
        • EBITDA: {int(profit * 1.2):,}€
        
        ANÁLISIS DE INGRESOS
        
        Los ingresos del período se han incrementado un {random.randint(5, 25)}% respecto 
        al trimestre anterior, impulsados principalmente por:
        
        1. Aumento en servicios de consultoría tecnológica (+{random.randint(10, 30)}%)
        2. Nuevos contratos de desarrollo de software (+{random.randint(15, 35)}%)
        3. Servicios de mantenimiento recurrentes (+{random.randint(5, 15)}%)
        
        ESTRUCTURA DE COSTOS
        
        Los principales componentes del costo operativo son:
        
        • Personal: {int(costs * 0.50):,}€ ({50}%)
        • Infraestructura tecnológica: {int(costs * 0.25):,}€ ({25}%)
        • Marketing y ventas: {int(costs * 0.15):,}€ ({15}%)
        • Gastos generales: {int(costs * 0.10):,}€ ({10}%)
        
        PROYECCIONES
        
        Para el próximo trimestre se estima un crecimiento del {random.randint(10, 20)}% 
        en ingresos, manteniendo los costos operativos en niveles similares, lo que 
        resultaría en una mejora significativa del margen de beneficio.
        
        CONCLUSIONES
        
        La compañía mantiene una posición financiera sólida con liquidez suficiente 
        para afrontar sus compromisos de corto plazo y continuar con el plan de 
        expansión establecido.
        """
        
        return {
            "title": random.choice(titles),
            "content": content,
            "metadata": {
                "report_type": "Financial",
                "period": f"Q{random.randint(1,4)}/{datetime.now().year}",
                "revenue": revenue,
                "profit": profit,
                "margin": round(profit/revenue*100, 2)
            }
        }
    
    def _generate_hr_content(self, doc_number: int) -> Dict:
        """Generate HR document content"""
        employee_name = random.choice([
            "María García López", "Juan Martínez Sánchez", "Ana Rodríguez Pérez",
            "Carlos Fernández González", "Laura Jiménez Díaz"
        ])
        
        position = random.choice([
            "Desarrollador Senior", "Analista de Datos", "Ingeniero DevOps",
            "Product Manager", "UX Designer", "Arquitecto de Software"
        ])
        
        salary = random.randint(35000, 75000)
        
        content = f"""
        OFERTA DE EMPLEO
        
        Fecha: {datetime.now().strftime('%d de %B de %Y')}
        Referencia: HRO-{doc_number:06d}
        
        DATOS DEL CANDIDATO
        
        Nombre completo: {employee_name}
        Puesto ofrecido: {position}
        Departamento: Tecnología e Innovación
        Ubicación: Madrid, España (Modalidad híbrida)
        
        CONDICIONES DE LA OFERTA
        
        1. RETRIBUCIÓN
        Salario bruto anual: {salary:,}€
        Bonus por objetivos: Hasta {int(salary * 0.15):,}€
        Retribución total estimada: {int(salary * 1.15):,}€
        
        2. BENEFICIOS SOCIALES
        • Seguro médico privado para empleado y familia
        • Ticket restaurant de 11€/día laboral
        • Plan de pensiones con aportación empresa del 3%
        • Programa de formación continua (presupuesto anual 2.000€)
        • Flexibilidad horaria y teletrabajo 3 días/semana
        • 25 días laborables de vacaciones anuales
        • Día libre de cumpleaños
        
        3. JORNADA Y HORARIO
        Jornada completa de 40 horas semanales
        Horario flexible de entrada: 8:00 - 10:00
        Horario flexible de salida: 17:00 - 19:00
        Viernes jornada intensiva hasta las 15:00
        
        4. INCORPORACIÓN
        Fecha prevista de incorporación: {
            (datetime.now().replace(day=1) + 
             __import__('relativedelta', fromlist=['relativedelta']).relativedelta(months=1)
            ).strftime('%d/%m/%Y') if False else '01/12/2025'
        }
        Período de prueba: 6 meses
        
        5. DESARROLLO PROFESIONAL
        • Plan de carrera personalizado
        • Participación en proyectos de I+D+i
        • Acceso a certificaciones profesionales
        • Posibilidad de rotación entre equipos
        
        6. REQUISITOS PARA LA ACEPTACIÓN
        Para aceptar esta oferta, el candidato deberá:
        - Firmar el presente documento
        - Aportar documentación requerida (DNI, titulación, certificados)
        - Superar el reconocimiento médico previo
        - Completar los trámites administrativos de alta
        
        Esta oferta tiene una validez de 15 días naturales desde su emisión.
        
        FinancIA 2030 S.L.
        Departamento de Recursos Humanos
        """
        
        return {
            "title": f"Oferta de Empleo - {position} #{doc_number}",
            "content": content,
            "metadata": {
                "offer_type": "Employment",
                "position": position,
                "salary": salary,
                "candidate_name": employee_name,
                "department": "Technology"
            }
        }
    
    def _generate_technical_content(self, doc_number: int) -> Dict:
        """Generate technical document content"""
        project_name = f"Proyecto {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])} #{doc_number}"
        
        content = f"""
        ESPECIFICACIÓN TÉCNICA
        Proyecto: {project_name}
        Versión: {random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}
        
        1. INTRODUCCIÓN
        
        Este documento describe la arquitectura técnica y especificaciones del sistema de 
        gestión documental con capacidades de inteligencia artificial desarrollado para 
        FinancIA 2030.
        
        2. ARQUITECTURA DEL SISTEMA
        
        2.1 Stack Tecnológico
        • Backend: FastAPI (Python 3.11+)
        • Frontend: React 18 con TypeScript
        • Base de datos: PostgreSQL 16 con pgvector
        • Búsqueda: OpenSearch 2.11
        • Storage: MinIO (S3-compatible)
        • Cache: Redis 7
        • Containers: Docker con GPU support
        
        2.2 Componentes Principales
        
        A) Motor de Procesamiento de Documentos
        - OCR con Tesseract 5.0
        - Extracción de entidades (NER) con spaCy
        - Clasificación automática con BERT
        - Generación de embeddings con sentence-transformers
        
        B) Sistema de Búsqueda Híbrida
        - Búsqueda léxica con BM25
        - Búsqueda semántica con vectores (768 dimensiones)
        - Ranking combinado con RRF (Reciprocal Rank Fusion)
        
        C) Módulo RAG (Retrieval-Augmented Generation)
        - Integración con OpenAI GPT-4
        - Context window de 8K tokens
        - Citación obligatoria de fuentes
        - Streaming de respuestas
        
        3. REQUISITOS DEL SISTEMA
        
        3.1 Hardware Mínimo
        • CPU: 8 cores
        • RAM: 16 GB
        • GPU: NVIDIA con 8GB VRAM (opcional pero recomendado)
        • Almacenamiento: 500 GB SSD
        
        3.2 Software
        • Docker 24+ con NVIDIA Container Toolkit
        • Docker Compose 2.20+
        • CUDA 12.6+ (para GPU)
        
        4. CONFIGURACIÓN Y DESPLIEGUE
        
        4.1 Variables de Entorno
        Las siguientes variables deben configurarse en el archivo .env:
        
        - DATABASE_URL: Conexión a PostgreSQL
        - REDIS_URL: Conexión a Redis
        - OPENSEARCH_HOST: Host de OpenSearch
        - MINIO_ENDPOINT: Endpoint de MinIO
        - OPENAI_API_KEY: API key de OpenAI
        
        4.2 Proceso de Despliegue
        1. Clonar repositorio
        2. Configurar variables de entorno
        3. Ejecutar: docker-compose up -d
        4. Verificar healthchecks
        5. Ejecutar migraciones: docker exec backend alembic upgrade head
        
        5. SEGURIDAD
        
        5.1 Autenticación y Autorización
        • JWT tokens con expiración de 30 minutos
        • Roles: admin, agent, user
        • Refresh tokens con rotación
        • Rate limiting por endpoint
        
        5.2 Protección de Datos
        • Encriptación en reposo (AES-256)
        • TLS 1.3 para comunicaciones
        • Audit logging completo
        • Cumplimiento GDPR/LOPDGDD
        
        6. MONITORIZACIÓN
        
        • Arize Phoenix para observabilidad LLM
        • Métricas de performance con Prometheus
        • Logs centralizados
        • Alertas automáticas
        
        7. PRUEBAS Y QA
        
        • Unit tests con pytest (cobertura >80%)
        • Integration tests
        • Performance tests con Locust
        • Security scanning con Trivy
        
        8. DOCUMENTACIÓN ADICIONAL
        
        Para más información, consultar:
        • API Reference: /docs (Swagger UI)
        • Architecture Decision Records (ADR)
        • Deployment Guide
        • User Manual
        """
        
        return {
            "title": f"Especificación Técnica - {project_name}",
            "content": content,
            "metadata": {
                "doc_type": "Technical Specification",
                "project": project_name,
                "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
                "stack": ["Python", "React", "PostgreSQL", "Docker"]
            }
        }
    
    def _generate_marketing_content(self, doc_number: int) -> Dict:
        """Generate marketing document content"""
        campaign_name = f"Campaña {random.choice(['Digital', 'Social', 'Email', 'Content'])} #{doc_number}"
        
        content = f"""
        PLAN DE MARKETING DIGITAL
        Campaña: {campaign_name}
        Período: Q{random.randint(1,4)}/{datetime.now().year}
        
        RESUMEN EJECUTIVO
        
        Plan estratégico de marketing digital enfocado en incrementar la visibilidad de 
        FinancIA 2030 en el mercado de soluciones documentales corporativas con IA.
        
        OBJETIVOS
        
        1. Aumentar el tráfico web en un {random.randint(30, 50)}%
        2. Generar {random.randint(100, 300)} leads cualificados
        3. Incrementar la tasa de conversión al {random.randint(3, 8)}%
        4. Mejorar el engagement en redes sociales (+{random.randint(40, 60)}%)
        
        PRESUPUESTO
        
        Presupuesto total: {random.randint(20000, 50000):,}€
        Distribución:
        • Google Ads: {random.randint(30, 40)}%
        • LinkedIn Ads: {random.randint(20, 30)}%
        • Content Marketing: {random.randint(15, 25)}%
        • Email Marketing: {random.randint(10, 15)}%
        • Diseño y creatividad: {random.randint(10, 15)}%
        
        ESTRATEGIA DE CONTENIDO
        
        Pilares de contenido:
        1. Inteligencia Artificial aplicada a documentos
        2. Transformación digital corporativa
        3. Compliance y seguridad documental
        4. Casos de éxito y testimonios
        
        CALENDARIO EDITORIAL
        
        • 2 blog posts semanales
        • 5 publicaciones en LinkedIn por semana
        • 1 webinar mensual
        • 1 whitepaper trimestral
        • Newsletter quincenal
        
        KPIs Y MÉTRICAS
        
        • Visitas web: {random.randint(5000, 15000)} mensuales
        • CTR medio: >{random.randint(2, 5)}%
        • CPL objetivo: <{random.randint(50, 150)}€
        • ROI esperado: {random.randint(200, 400)}%
        """
        
        return {
            "title": f"Plan de Marketing - {campaign_name}",
            "content": content,
            "metadata": {
                "campaign_type": "Digital Marketing",
                "budget": random.randint(20000, 50000),
                "duration_months": 3,
                "channels": ["Google Ads", "LinkedIn", "Email", "Content"]
            }
        }
    
    def _generate_operations_content(self, doc_number: int) -> Dict:
        """Generate operations document content"""
        content = f"""
        PROCEDIMIENTO OPERATIVO ESTÁNDAR (SOP)
        ID: SOP-{doc_number:06d}
        Versión: 1.{random.randint(0, 9)}
        
        TÍTULO: Gestión de Incidencias en Producción
        
        1. PROPÓSITO
        
        Establecer un procedimiento estandarizado para la detección, clasificación, 
        resolución y documentación de incidencias en el entorno de producción.
        
        2. ALCANCE
        
        Este procedimiento aplica a todos los miembros del equipo técnico y operaciones 
        de FinancIA 2030, incluyendo desarrolladores, DevOps y soporte.
        
        3. CLASIFICACIÓN DE INCIDENCIAS
        
        • Crítica (P1): Servicio caído, pérdida de datos
        • Alta (P2): Funcionalidad principal afectada
        • Media (P3): Funcionalidad secundaria afectada
        • Baja (P4): Mejoras o bugs menores
        
        4. TIEMPOS DE RESPUESTA (SLA)
        
        • P1: Respuesta inmediata, resolución en 2 horas
        • P2: Respuesta en 1 hora, resolución en 8 horas
        • P3: Respuesta en 4 horas, resolución en 48 horas
        • P4: Respuesta en 24 horas, resolución en 5 días
        
        5. PROCEDIMIENTO
        
        5.1 Detección
        - Monitorización automática (alertas)
        - Reporte de usuarios
        - Auditorías programadas
        
        5.2 Registro
        - Crear ticket en sistema de gestión
        - Asignar prioridad y categoría
        - Notificar a equipo responsable
        
        5.3 Análisis
        - Revisar logs y métricas
        - Identificar causa raíz
        - Evaluar impacto
        
        5.4 Resolución
        - Implementar fix o workaround
        - Validar en entorno de staging
        - Desplegar a producción
        - Verificar resolución
        
        5.5 Cierre
        - Documentar solución aplicada
        - Actualizar base de conocimiento
        - Notificar a stakeholders
        - Realizar post-mortem si procede
        
        6. COMUNICACIÓN
        
        • Incidencias P1/P2: Notificación inmediata a management
        • Status updates cada 30 minutos para P1
        • Comunicado post-resolución para todos
        
        7. ESCALADO
        
        Si no se resuelve en el tiempo SLA:
        - P1: Escalar a CTO inmediatamente
        - P2: Escalar después de 4 horas
        - P3/P4: Escalar después de 2 días
        
        8. MÉTRICAS
        
        • MTTR (Mean Time To Repair)
        • MTBF (Mean Time Between Failures)
        • Cumplimiento SLA
        • Satisfacción del usuario
        """
        
        return {
            "title": f"SOP - Gestión de Incidencias #{doc_number}",
            "content": content,
            "metadata": {
                "sop_id": f"SOP-{doc_number:06d}",
                "version": f"1.{random.randint(0, 9)}",
                "department": "Operations",
                "review_date": datetime.now().strftime('%Y-%m-%d')
            }
        }
    
    def _generate_compliance_content(self, doc_number: int) -> Dict:
        """Generate compliance document content"""
        content = f"""
        INFORME DE AUDITORÍA DE CUMPLIMIENTO
        Referencia: AUD-{doc_number:06d}
        Fecha: {datetime.now().strftime('%d/%m/%Y')}
        
        DATOS DE LA AUDITORÍA
        
        Entidad Auditada: FinancIA 2030 S.L.
        Auditor: Despacho de Cumplimiento Legal SLP
        Período Auditado: {datetime.now().year}
        Normativas Aplicables: GDPR, LOPDGDD, ISO 27001, Esquema Nacional de Seguridad
        
        RESUMEN EJECUTIVO
        
        Se ha realizado una auditoría exhaustiva de los sistemas y procedimientos de 
        FinancIA 2030 para verificar el cumplimiento de la normativa aplicable en 
        materia de protección de datos, seguridad de la información y privacidad.
        
        HALLAZGOS PRINCIPALES
        
        1. PROTECCIÓN DE DATOS (GDPR/LOPDGDD)
        
        Fortalezas identificadas:
        ✓ Registro de Actividades de Tratamiento completo y actualizado
        ✓ Análisis de Riesgos (DPIA) realizado para tratamientos de alto riesgo
        ✓ Contratos con encargados de tratamiento correctamente formalizados
        ✓ Política de privacidad clara y accesible
        ✓ Procedimientos de ejercicio de derechos ARCO implementados
        
        Áreas de mejora:
        • Actualizar el procedimiento de notificación de brechas de seguridad
        • Reforzar la formación en protección de datos del personal
        • Revisar los plazos de conservación de algunos tratamientos
        
        2. SEGURIDAD DE LA INFORMACIÓN (ISO 27001)
        
        Fortalezas identificadas:
        ✓ Política de seguridad aprobada y comunicada
        ✓ Control de accesos basado en roles implementado
        ✓ Cifrado de datos en reposo y en tránsito
        ✓ Copias de seguridad automatizadas y probadas
        ✓ Logs de auditoría completos
        
        Áreas de mejora:
        • Implementar autenticación multifactor para todos los usuarios
        • Realizar pentesting externo anualmente
        • Documentar el plan de continuidad de negocio
        
        3. DERECHOS DIGITALES
        
        Fortalezas identificadas:
        ✓ Sistema de anonimización de datos personales
        ✓ Procedimiento de desconexión digital
        ✓ Transparencia en el uso de sistemas automatizados de decisión
        
        4. CUMPLIMIENTO TÉCNICO
        
        Estado de las medidas de seguridad:
        
        Nivel Básico: CONFORME (100%)
        Nivel Medio: CONFORME (95%)
        Nivel Alto: EN PROGRESO (85%)
        
        RECOMENDACIONES
        
        1. CORTO PLAZO (1-3 meses)
        • Actualizar procedimiento de brechas de seguridad
        • Implementar MFA para accesos críticos
        • Reforzar formación en protección de datos
        
        2. MEDIO PLAZO (3-6 meses)
        • Realizar pentesting externo
        • Completar certificación ISO 27001
        • Documentar plan de continuidad de negocio
        
        3. LARGO PLAZO (6-12 meses)
        • Obtener certificaciones adicionales (ENS, ISO 27701)
        • Implementar DLP (Data Loss Prevention)
        • Establecer programa de bug bounty
        
        CONCLUSIÓN
        
        FinancIA 2030 mantiene un nivel de cumplimiento satisfactorio ({random.randint(85, 95)}%) 
        de la normativa aplicable. Las recomendaciones propuestas permitirán alcanzar 
        la excelencia en materia de compliance y seguridad de la información.
        
        Calificación Global: {'FAVORABLE' if random.random() > 0.3 else 'FAVORABLE CON OBSERVACIONES'}
        
        Próxima Auditoría: {datetime.now().replace(year=datetime.now().year + 1).strftime('%B %Y')}
        """
        
        return {
            "title": f"Informe de Auditoría de Cumplimiento #{doc_number}",
            "content": content,
            "metadata": {
                "audit_id": f"AUD-{doc_number:06d}",
                "audit_date": datetime.now().strftime('%Y-%m-%d'),
                "compliance_score": random.randint(85, 95),
                "standards": ["GDPR", "ISO27001", "ENS", "LOPDGDD"]
            }
        }
    
    async def generate_document(self, category: str, doc_number: int, output_dir: Path) -> Dict:
        """Generate a single document PDF"""
        try:
            # Generate content
            generator = self.categories.get(category)
            if not generator:
                raise ValueError(f"Unknown category: {category}")
            
            doc_data = generator(doc_number)
            
            # Create PDF
            filename = f"{category}_{doc_number:06d}.pdf"
            filepath = output_dir / filename
            
            # Create PDF document
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            )
            
            # Build PDF content
            story = []
            
            # Add title
            story.append(Paragraph(doc_data['title'], title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Add content paragraphs
            for paragraph in doc_data['content'].strip().split('\n\n'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip().replace('\n', '<br/>'), body_style))
                    story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(story)
            
            # Get file size
            file_size = filepath.stat().st_size
            
            # Save metadata JSON
            import json
            metadata_filepath = filepath.with_suffix('.json')
            metadata_content = {
                "title": doc_data['title'],
                "category": category,
                "file_size": file_size,
                "entities": doc_data['metadata'].get('entities', []),
                "risk_level": doc_data['metadata'].get('risk_level', 'medium'),
                "chunks": len(doc_data['content'].split('\n\n')),
                "created_at": datetime.now().isoformat(),
                "metadata": doc_data['metadata']
            }
            with open(metadata_filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata_content, f, indent=2, ensure_ascii=False)
            
            # Save text preview
            txt_filepath = filepath.with_suffix('.txt')
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(doc_data['content'])
            
            return {
                "filename": filename,
                "filepath": str(filepath),
                "category": category,
                "title": doc_data['title'],
                "size": file_size,
                "metadata": doc_data['metadata'],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating document {category}_{doc_number}: {e}")
            raise


class FullSyntheticDataService:
    """Full service for generating and managing synthetic documents"""
    
    def __init__(self):
        self.generator = SyntheticDocumentGenerator()
        self.tasks = {}
        self.output_base_dir = Path("/tmp/synthetic_documents")
        self.output_base_dir.mkdir(exist_ok=True)
    
    def calculate_distribution(self, template_id: str, total_documents: int) -> Dict[str, int]:
        """Calculate document distribution based on template"""
        templates = {
            "default": {
                "Legal": 0.25,
                "Financial": 0.20,
                "HR": 0.15,
                "Technical": 0.15,
                "Marketing": 0.10,
                "Operations": 0.10,
                "Compliance": 0.05
            },
            "financial": {
                "Financial": 0.40,
                "Legal": 0.25,
                "Compliance": 0.20,
                "Operations": 0.15
            },
            "contracts": {
                "Legal": 0.50,
                "Compliance": 0.30,
                "Financial": 0.20
            }
        }
        
        distribution = templates.get(template_id, templates["default"])
        
        # Calculate absolute numbers
        result = {}
        remaining = total_documents
        
        for category, percentage in distribution.items():
            count = int(total_documents * percentage)
            result[category] = count
            remaining -= count
        
        # Distribute remaining documents to first category
        if remaining > 0:
            first_category = list(result.keys())[0]
            result[first_category] += remaining
        
        return result
    
    async def generate_async(
        self, 
        total_documents: int = 50, 
        categories: Optional[Dict[str, int]] = None,
        auto_upload: bool = False,
        user_id: Optional[str] = None
    ) -> str:
        """Start async generation of synthetic documents"""
        task_id = str(uuid.uuid4())
        
        # Create task directory
        task_dir = self.output_base_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        # Initialize task
        self.tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "progress": 0,
            "total_documents": total_documents,
            "generated_documents": 0,
            "user_id": user_id,
            "categories": categories or {},
            "created_at": datetime.utcnow().isoformat(),
            "output_path": str(task_dir),
            "files": [],
            "error": None
        }
        
        # Start generation in background
        asyncio.create_task(self._generate_documents(task_id, categories, task_dir))
        
        return task_id
    
    async def _generate_documents(
        self, 
        task_id: str, 
        categories: Dict[str, int],
        output_dir: Path
    ):
        """Background task to generate documents"""
        try:
            task = self.tasks[task_id]
            task["status"] = "running"
            
            total = sum(categories.values())
            generated = 0
            files = []
            
            # Generate documents for each category
            for category, count in categories.items():
                for i in range(count):
                    try:
                        doc_info = await self.generator.generate_document(
                            category, 
                            generated + 1,
                            output_dir
                        )
                        files.append(doc_info)
                        generated += 1
                        
                        # Update progress
                        task["generated_documents"] = generated
                        task["progress"] = int((generated / total) * 100)
                        task["files"] = files
                        
                        # Small delay to avoid overwhelming the system
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error generating document {category}_{i}: {e}")
                        continue
            
            # Mark as completed
            task["status"] = "completed"
            task["progress"] = 100
            
            logger.info(f"Task {task_id} completed: {generated} documents generated")
            
        except Exception as e:
            logger.error(f"Error in generation task {task_id}: {e}")
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = str(e)
    
    async def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        
        return {
            "task_id": task_id,
            "status": task.get("status", "pending"),
            "progress": task.get("progress", 0),
            "documents_generated": task.get("generated_documents", 0),
            "total_documents": task.get("total_documents", 0),
            "created_at": task.get("created_at", datetime.utcnow().isoformat()),
            "output_path": task.get("output_path"),
            "error": task.get("error"),
            "documents_uploaded": task.get("documents_uploaded"),
            "files": task.get("files", [])
        }
    
    async def list_tasks(self, user_id: Optional[str] = None) -> List[Dict]:
        """List all tasks for a user"""
        tasks = []
        for task_id, task in self.tasks.items():
            if user_id is None or task.get("user_id") == user_id:
                tasks.append({
                    "task_id": task_id,
                    "status": task.get("status", "pending"),
                    "progress": task.get("progress", 0),
                    "documents_generated": task.get("generated_documents", 0),
                    "total_documents": task.get("total_documents", 0),
                    "created_at": task.get("created_at", datetime.utcnow().isoformat()),
                    "output_path": task.get("output_path")
                })
        return tasks
    
    async def get_task_files(self, task_id: str) -> List[Dict]:
        """Get list of files generated for a task"""
        task = self.tasks.get(task_id)
        if not task:
            return []
        
        return task.get("files", [])
    
    def get_templates(self) -> Dict:
        """Get available templates"""
        return {
            "default": {
                "name": "Default distribution",
                "description": "Balanced distribution across all categories",
                "categories": {
                    "Legal": 0.25,
                    "Financial": 0.20,
                    "HR": 0.15,
                    "Technical": 0.15,
                    "Marketing": 0.10,
                    "Operations": 0.10,
                    "Compliance": 0.05
                }
            },
            "financial": {
                "name": "Financial documents focus",
                "description": "Emphasizes financial and compliance documents",
                "categories": {
                    "Financial": 0.40,
                    "Legal": 0.25,
                    "Compliance": 0.20,
                    "Operations": 0.15
                }
            },
            "contracts": {
                "name": "Contract documents focus",
                "description": "Emphasizes legal and compliance documents",
                "categories": {
                    "Legal": 0.50,
                    "Compliance": 0.30,
                    "Financial": 0.20
                }
            }
        }
    
    def get_available_templates(self) -> Dict:
        """Alias for get_templates"""
        return self.get_templates()
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task and its associated files"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        try:
            # Delete files if they exist
            output_path = task.get("output_path")
            if output_path:
                output_dir = Path(output_path)
                if output_dir.exists() and output_dir.is_dir():
                    import shutil
                    shutil.rmtree(output_dir)
                    logger.info(f"Deleted output directory for task {task_id}")
            
            # Remove from tasks dict
            del self.tasks[task_id]
            logger.info(f"Task {task_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False


# Create service instance
synthetic_data_service = FullSyntheticDataService()

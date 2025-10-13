#!/usr/bin/env python3
"""
Script para generar PDFs de ejemplo para el entorno de demostración.
Crea documentos PDF realistas con contenido de muestra.

Requisitos:
    pip install reportlab pillow

Uso:
    python generate_sample_pdfs.py
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, red, blue, green
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from pathlib import Path


# Configuración
OUTPUT_DIR = Path(__file__).parent.parent / "sample-documents"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def add_header_footer(canvas, doc, title):
    """Agregar header y footer a cada página"""
    canvas.saveState()
    
    # Header
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(inch, letter[1] - 0.5*inch, title)
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(letter[0] - inch, letter[1] - 0.5*inch, 
                          f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.drawString(inch, 0.5*inch, "Sistema Documental Corporativo - Demo")
    canvas.drawRightString(letter[0] - inch, 0.5*inch, f"Página {doc.page}")
    
    canvas.restoreState()


def generate_manual_procedimientos():
    """Generar Manual de Procedimientos Corporativos (127 páginas)"""
    print("📄 Generando: Manual de Procedimientos Corporativos...")
    
    filename = OUTPUT_DIR / "manual_procedimientos.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter,
                           topMargin=1*inch, bottomMargin=1*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=24, textColor=HexColor('#1e40af'),
                                 spaceAfter=30, alignment=TA_CENTER)
    
    story = []
    
    # Portada
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Manual de Procedimientos Corporativos", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Versión 3.1", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d de %B de %Y')}", styles['Normal']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Dirección de Calidad", styles['Heading3']))
    story.append(PageBreak())
    
    # Índice
    story.append(Paragraph("Índice", styles['Heading1']))
    story.append(Spacer(1, 0.3*inch))
    
    sections = [
        ("1. Introducción", 3),
        ("2. Alcance y Objetivos", 5),
        ("3. Definiciones y Términos", 8),
        ("4. Procedimientos Administrativos", 12),
        ("5. Procedimientos Operacionales", 45),
        ("6. Gestión de Documentos", 78),
        ("7. Control de Calidad", 95),
        ("8. Auditorías y Revisiones", 110),
        ("9. Mejora Continua", 120),
        ("10. Anexos", 125),
    ]
    
    for section, page in sections:
        story.append(Paragraph(f"{section} {'.' * 50} {page}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # Contenido de ejemplo
    for i, (section_title, _) in enumerate(sections, 1):
        story.append(Paragraph(section_title, styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        # Agregar párrafos de contenido
        for j in range(3):
            content = f"""
            Este es el contenido de la sección {section_title}. En esta parte del manual 
            se describen los procedimientos y lineamientos necesarios para asegurar el correcto 
            funcionamiento de los procesos corporativos. Es importante seguir estos procedimientos 
            de manera consistente para mantener los estándares de calidad establecidos por la 
            organización y cumplir con las normativas vigentes ISO 9001:2015.
            
            Los responsables de cada área deben asegurarse de que todo el personal bajo su cargo 
            conozca y aplique correctamente estos procedimientos. Se requiere una revisión periódica 
            de estos documentos para garantizar su vigencia y relevancia.
            """
            story.append(Paragraph(content, styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        # Tabla de ejemplo cada 2 secciones
        if i % 2 == 0:
            data = [
                ['Actividad', 'Responsable', 'Frecuencia', 'Registro'],
                ['Revisión de documentos', 'Jefe de Área', 'Mensual', 'FOR-001'],
                ['Auditoría interna', 'Calidad', 'Trimestral', 'FOR-002'],
                ['Capacitación personal', 'RRHH', 'Semestral', 'FOR-003'],
            ]
            
            t = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f3f4f6')),
                ('GRID', (0, 0), (-1, -1), 1, black),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
    
    # Construir PDF
    doc.build(story, onFirstPage=lambda c, d: add_header_footer(c, d, "Manual de Procedimientos"),
              onLaterPages=lambda c, d: add_header_footer(c, d, "Manual de Procedimientos"))
    
    print(f"   ✅ Creado: {filename}")
    return filename


def generate_politica_seguridad():
    """Generar Política de Seguridad de la Información (45 páginas)"""
    print("📄 Generando: Política de Seguridad de la Información...")
    
    filename = OUTPUT_DIR / "politica_seguridad.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter,
                           topMargin=1*inch, bottomMargin=1*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=24, textColor=HexColor('#dc2626'),
                                 spaceAfter=30, alignment=TA_CENTER)
    
    story = []
    
    # Portada
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Política de Seguridad<br/>de la Información", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Versión 2.0 - BORRADOR", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("🔒 DOCUMENTO CONFIDENCIAL", ParagraphStyle('Confidential', 
                 parent=styles['Normal'], textColor=red, fontSize=14, alignment=TA_CENTER)))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Chief Information Security Officer (CISO)", styles['Heading3']))
    story.append(PageBreak())
    
    # Contenido
    sections = [
        "1. Objetivo y Alcance",
        "2. Marco Normativo ISO 27001",
        "3. Clasificación de la Información",
        "4. Control de Acceso",
        "5. Gestión de Contraseñas",
        "6. Seguridad en Redes",
        "7. Protección de Datos Personales",
        "8. Respuesta a Incidentes",
        "9. Continuidad del Negocio",
        "10. Cumplimiento y Auditoría",
    ]
    
    for section in sections:
        story.append(Paragraph(section, styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        for _ in range(2):
            content = f"""
            <b>{section}</b> establece las directrices y controles necesarios para proteger 
            los activos de información de la organización contra amenazas internas y externas. 
            Esta política se basa en las mejores prácticas de la norma ISO/IEC 27001:2022 y 
            aplica a todos los empleados, contratistas y terceros que tengan acceso a los 
            sistemas de información corporativos.
            
            Es responsabilidad de cada usuario cumplir con estas políticas y reportar cualquier 
            incidente de seguridad de manera inmediata al área de TI. El incumplimiento de estas 
            políticas puede resultar en acciones disciplinarias según el reglamento interno.
            """
            story.append(Paragraph(content, styles['BodyText']))
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
    
    doc.build(story, onFirstPage=lambda c, d: add_header_footer(c, d, "Política de Seguridad"),
              onLaterPages=lambda c, d: add_header_footer(c, d, "Política de Seguridad"))
    
    print(f"   ✅ Creado: {filename}")
    return filename


def generate_reporte_financiero():
    """Generar Reporte Financiero Q3 2025 (89 páginas)"""
    print("📄 Generando: Reporte Financiero Q3 2025...")
    
    filename = OUTPUT_DIR / "reporte_financiero_q3_2025.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter,
                           topMargin=1*inch, bottomMargin=1*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=24, textColor=HexColor('#059669'),
                                 spaceAfter=30, alignment=TA_CENTER)
    
    story = []
    
    # Portada
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Reporte Financiero<br/>Q3 2025", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Tercer Trimestre - Julio a Septiembre", styles['Heading2']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Dirección Financiera", styles['Heading3']))
    story.append(PageBreak())
    
    # Resumen Ejecutivo
    story.append(Paragraph("Resumen Ejecutivo", styles['Heading1']))
    story.append(Spacer(1, 0.3*inch))
    
    summary = """
    El tercer trimestre de 2025 presenta resultados sobresalientes con un crecimiento del 
    15% respecto al trimestre anterior (Q2 2025) y un 23% de crecimiento interanual. 
    Los ingresos totales alcanzaron $45.7 millones, superando las proyecciones en un 8%.
    
    La rentabilidad operacional se mantiene saludable con un EBITDA de $12.3 millones 
    (margen del 27%), mejorando 2 puntos porcentuales respecto al trimestre anterior.
    """
    story.append(Paragraph(summary, styles['BodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Tabla de métricas clave
    data = [
        ['Métrica', 'Q3 2025', 'Q2 2025', 'Var. %'],
        ['Ingresos Totales', '$45.7M', '$39.7M', '+15%'],
        ['EBITDA', '$12.3M', '$9.8M', '+26%'],
        ['Margen EBITDA', '27%', '25%', '+2pp'],
        ['Utilidad Neta', '$8.9M', '$7.2M', '+24%'],
        ['ROE', '18.5%', '16.2%', '+2.3pp'],
    ]
    
    t = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#d1fae5')),
        ('GRID', (0, 0), (-1, -1), 1, black),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # Agregar más secciones
    sections = [
        "Análisis de Ingresos",
        "Estructura de Costos",
        "Flujo de Caja",
        "Balance General",
        "Análisis de Ratios",
        "Proyecciones Q4 2025",
    ]
    
    for section in sections:
        story.append(Paragraph(section, styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        for _ in range(3):
            content = f"""
            En la sección de {section}, se presenta un análisis detallado de los principales 
            indicadores financieros del trimestre. Los resultados reflejan una gestión eficiente 
            de los recursos y una estrategia comercial efectiva que ha permitido incrementar 
            la participación de mercado en un 12% durante el período analizado.
            """
            story.append(Paragraph(content, styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
    
    doc.build(story, onFirstPage=lambda c, d: add_header_footer(c, d, "Reporte Financiero Q3 2025"),
              onLaterPages=lambda c, d: add_header_footer(c, d, "Reporte Financiero Q3 2025"))
    
    print(f"   ✅ Creado: {filename}")
    return filename


def generate_contrato():
    """Generar Contrato de Servicio - Cliente XYZ (23 páginas)"""
    print("📄 Generando: Contrato de Servicio - Cliente XYZ...")
    
    filename = OUTPUT_DIR / "contrato_xyz_2025.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter,
                           topMargin=1*inch, bottomMargin=1*inch)
    
    styles = getSampleStyleSheet()
    
    story = []
    
    # Portada
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("CONTRATO DE PRESTACIÓN DE SERVICIOS", styles['Heading1']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Contrato No. XYZ-2025-001", styles['Heading2']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Cliente: XYZ Corporation", styles['Normal']))
    story.append(Paragraph("Vigencia: 01/01/2025 - 31/12/2025", styles['Normal']))
    story.append(Paragraph("Valor: $150,000 USD", styles['Normal']))
    story.append(PageBreak())
    
    # Cláusulas
    clauses = [
        ("PRIMERA - OBJETO DEL CONTRATO", 
         "El presente contrato tiene por objeto la prestación de servicios profesionales..."),
        ("SEGUNDA - PLAZO Y VIGENCIA", 
         "El plazo de vigencia del presente contrato será de doce (12) meses..."),
        ("TERCERA - VALOR Y FORMA DE PAGO", 
         "El valor total del contrato es de CIENTO CINCUENTA MIL DÓLARES ($150,000 USD)..."),
        ("CUARTA - OBLIGACIONES DEL CONTRATISTA", 
         "El contratista se obliga a cumplir con todas las especificaciones técnicas..."),
        ("QUINTA - OBLIGACIONES DEL CONTRATANTE", 
         "El contratante se compromete a facilitar el acceso a las instalaciones..."),
        ("SEXTA - CONFIDENCIALIDAD", 
         "Las partes se obligan a mantener confidencialidad sobre toda información..."),
        ("SÉPTIMA - PROPIEDAD INTELECTUAL", 
         "Todos los derechos de propiedad intelectual generados durante la ejecución..."),
        ("OCTAVA - TERMINACIÓN ANTICIPADA", 
         "Cualquiera de las partes podrá dar por terminado el contrato con 30 días..."),
        ("NOVENA - SOLUCIÓN DE CONTROVERSIAS", 
         "Las controversias que surjan serán resueltas mediante arbitraje..."),
        ("DÉCIMA - DISPOSICIONES GENERALES", 
         "Para todos los efectos legales, las partes acuerdan someterse..."),
    ]
    
    for title, content in clauses:
        story.append(Paragraph(f"CLÁUSULA {title}", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        full_content = f"""
        {content} Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
        nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu 
        fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in 
        culpa qui officia deserunt mollit anim id est laborum.
        """
        story.append(Paragraph(full_content, styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))
    
    # Firmas
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("En constancia de lo anterior, las partes firman:", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    signature_data = [
        ['EL CONTRATANTE', 'EL CONTRATISTA'],
        ['', ''],
        ['_____________________', '_____________________'],
        ['Nombre: [REDACTED]', 'Nombre: [REDACTED]'],
        ['CC: [REDACTED]', 'CC: [REDACTED]'],
    ]
    
    t = Table(signature_data, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t)
    
    doc.build(story, onFirstPage=lambda c, d: add_header_footer(c, d, "Contrato XYZ-2025"),
              onLaterPages=lambda c, d: add_header_footer(c, d, "Contrato XYZ-2025"))
    
    print(f"   ✅ Creado: {filename}")
    return filename


def generate_plan_estrategico():
    """Generar Plan Estratégico 2025-2027 (156 páginas)"""
    print("📄 Generando: Plan Estratégico 2025-2027...")
    
    filename = OUTPUT_DIR / "plan_estrategico_2025_2027.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter,
                           topMargin=1*inch, bottomMargin=1*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=24, textColor=HexColor('#7c3aed'),
                                 spaceAfter=30, alignment=TA_CENTER)
    
    story = []
    
    # Portada
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Plan Estratégico<br/>2025-2027", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Versión 2.1 - En Revisión", styles['Heading2']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Dirección General", styles['Heading3']))
    story.append(PageBreak())
    
    # Visión y Misión
    story.append(Paragraph("Visión 2027", styles['Heading1']))
    story.append(Spacer(1, 0.3*inch))
    vision = """
    Ser la empresa líder en transformación digital corporativa en América Latina, 
    reconocida por nuestra innovación, excelencia operacional y compromiso con la 
    sostenibilidad, alcanzando un crecimiento anual del 30% y una satisfacción del 
    cliente superior al 95%.
    """
    story.append(Paragraph(vision, styles['BodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("Misión", styles['Heading1']))
    story.append(Spacer(1, 0.3*inch))
    mission = """
    Proporcionar soluciones tecnológicas innovadoras que transformen la manera en que 
    nuestros clientes gestionan su información y procesos, mediante la aplicación de 
    inteligencia artificial, automatización y mejores prácticas internacionales.
    """
    story.append(Paragraph(mission, styles['BodyText']))
    story.append(PageBreak())
    
    # Objetivos Estratégicos
    story.append(Paragraph("Objetivos Estratégicos", styles['Heading1']))
    story.append(Spacer(1, 0.3*inch))
    
    objectives = [
        ("1. Transformación Digital", 
         "Implementar IA y automatización en 80% de procesos para 2027"),
        ("2. Crecimiento de Mercado", 
         "Aumentar participación de mercado del 12% al 25%"),
        ("3. Excelencia Operacional", 
         "Mejorar eficiencia operacional en 30% mediante optimización de procesos"),
        ("4. Desarrollo de Talento", 
         "Capacitar al 100% del personal en tecnologías emergentes"),
        ("5. Sostenibilidad", 
         "Reducir huella de carbono en 40% y lograr carbono-neutralidad"),
    ]
    
    for obj_title, obj_desc in objectives:
        story.append(Paragraph(f"<b>{obj_title}</b>", styles['Heading2']))
        story.append(Paragraph(obj_desc, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # KPIs
    story.append(Paragraph("Indicadores Clave de Desempeño (KPIs)", styles['Heading1']))
    story.append(Spacer(1, 0.3*inch))
    
    kpi_data = [
        ['KPI', 'Baseline 2024', 'Meta 2025', 'Meta 2026', 'Meta 2027'],
        ['Ingresos (M USD)', '$120', '$156', '$203', '$264'],
        ['Margen EBITDA', '25%', '27%', '29%', '32%'],
        ['NPS', '65', '72', '80', '88'],
        ['Empleados', '450', '550', '680', '850'],
        ['Procesos Automatizados', '30%', '50%', '65%', '80%'],
    ]
    
    t = Table(kpi_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ede9fe')),
        ('GRID', (0, 0), (-1, -1), 1, black),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # Iniciativas Estratégicas
    initiatives = [
        "Plataforma de IA Corporativa",
        "Expansión Internacional",
        "Centro de Innovación",
        "Programa de Sostenibilidad",
        "Academia Corporativa de Tecnología",
    ]
    
    for initiative in initiatives:
        story.append(Paragraph(f"Iniciativa: {initiative}", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        for _ in range(2):
            content = f"""
            La iniciativa {initiative} representa un pilar fundamental de nuestra estrategia 
            de crecimiento. Esta iniciativa requiere una inversión estimada de $5-8 millones 
            durante el período 2025-2027 y se espera que genere un ROI del 200% para finales 
            de 2027. El comité ejecutivo ha designado un líder de proyecto y un equipo 
            multidisciplinario para garantizar su éxito.
            """
            story.append(Paragraph(content, styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
    
    doc.build(story, onFirstPage=lambda c, d: add_header_footer(c, d, "Plan Estratégico 2025-2027"),
              onLaterPages=lambda c, d: add_header_footer(c, d, "Plan Estratégico 2025-2027"))
    
    print(f"   ✅ Creado: {filename}")
    return filename


def main():
    """Función principal"""
    print("=" * 70)
    print("📄 GENERADOR DE PDFs DE DEMOSTRACIÓN")
    print("=" * 70)
    print()
    
    try:
        # Verificar que reportlab esté instalado
        print("🔍 Verificando dependencias...")
        print("   ✓ reportlab disponible")
        print()
        
        print(f"📁 Directorio de salida: {OUTPUT_DIR}")
        print()
        
        # Generar todos los PDFs
        files_created = []
        
        files_created.append(generate_manual_procedimientos())
        files_created.append(generate_politica_seguridad())
        files_created.append(generate_reporte_financiero())
        files_created.append(generate_contrato())
        files_created.append(generate_plan_estrategico())
        
        print()
        print("=" * 70)
        print("✅ GENERACIÓN COMPLETADA")
        print("=" * 70)
        print()
        print(f"📊 Total de archivos creados: {len(files_created)}")
        print()
        print("Archivos generados:")
        for f in files_created:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"   • {f.name} ({size_mb:.2f} MB)")
        
        return 0
        
    except ImportError:
        print("❌ Error: reportlab no está instalado")
        print("   Ejecutar: pip install reportlab pillow")
        return 1
    except Exception as e:
        print(f"❌ Error al generar PDFs: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

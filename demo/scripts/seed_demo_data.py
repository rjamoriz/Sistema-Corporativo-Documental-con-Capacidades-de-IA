#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de demostración.
Crea usuarios, documentos, anotaciones y metadatos de prueba.

Uso:
    python seed_demo_data.py
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Agregar el path del backend al sys.path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

# Importar modelos (ajustar según tu estructura)
# from app.models import User, Document, Annotation, DocumentMetadata

# Configuración
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/documental_db")

# Datos de demo
DEMO_USERS = [
    {
        "username": "admin.demo",
        "email": "admin@demo.documental.com",
        "full_name": "Administrador Demo",
        "role": "ADMIN",
        "password": "Demo2025!",
        "department": "IT",
    },
    {
        "username": "revisor.demo",
        "email": "revisor@demo.documental.com",
        "full_name": "María Revisor",
        "role": "REVIEWER",
        "password": "Demo2025!",
        "department": "Calidad",
    },
    {
        "username": "usuario.demo",
        "email": "usuario@demo.documental.com",
        "full_name": "Juan Usuario",
        "role": "USER",
        "password": "Demo2025!",
        "department": "Operaciones",
    },
    {
        "username": "lectura.demo",
        "email": "lectura@demo.documental.com",
        "full_name": "Ana Lectura",
        "role": "VIEWER",
        "password": "Demo2025!",
        "department": "Auditoría",
    },
]

DEMO_DOCUMENTS = [
    {
        "title": "Manual de Procedimientos Corporativos",
        "filename": "manual_procedimientos.pdf",
        "file_path": "/storage/demo/manual_procedimientos.pdf",
        "file_size": 2457600,  # ~2.4 MB
        "mime_type": "application/pdf",
        "version": "3.1",
        "status": "APPROVED",
        "category": "Normativa",
        "tags": ["procedimientos", "normativa", "corporativo"],
        "description": "Manual completo de procedimientos administrativos y operacionales de la empresa.",
        "metadata": {
            "author": "Dirección de Calidad",
            "created_date": "2024-01-15",
            "last_review": "2025-09-01",
            "next_review": "2026-03-01",
            "confidentiality": "Internal",
            "page_count": 127,
        }
    },
    {
        "title": "Política de Seguridad de la Información",
        "filename": "politica_seguridad.pdf",
        "file_path": "/storage/demo/politica_seguridad.pdf",
        "file_size": 1048576,  # 1 MB
        "mime_type": "application/pdf",
        "version": "2.0",
        "status": "DRAFT",
        "category": "Seguridad",
        "tags": ["seguridad", "ISO27001", "políticas"],
        "description": "Política de seguridad de la información basada en ISO 27001.",
        "metadata": {
            "author": "CISO",
            "created_date": "2024-11-20",
            "last_review": "2025-10-05",
            "next_review": "2025-11-30",
            "confidentiality": "Confidential",
            "page_count": 45,
        }
    },
    {
        "title": "Reporte Financiero Q3 2025",
        "filename": "reporte_financiero_q3_2025.pdf",
        "file_path": "/storage/demo/reporte_financiero_q3_2025.pdf",
        "file_size": 3145728,  # 3 MB
        "mime_type": "application/pdf",
        "version": "1.0",
        "status": "APPROVED",
        "category": "Financiero",
        "tags": ["financiero", "reporte", "Q3", "2025"],
        "description": "Informe financiero del tercer trimestre 2025 con análisis de resultados.",
        "metadata": {
            "author": "Dirección Financiera",
            "created_date": "2025-09-30",
            "last_review": "2025-10-08",
            "next_review": "2025-12-31",
            "confidentiality": "Restricted",
            "page_count": 89,
        }
    },
    {
        "title": "Contrato de Servicio - Cliente XYZ",
        "filename": "contrato_xyz_2025.pdf",
        "file_path": "/storage/demo/contrato_xyz_2025.pdf",
        "file_size": 524288,  # 512 KB
        "mime_type": "application/pdf",
        "version": "1.2",
        "status": "APPROVED",
        "category": "Legal",
        "tags": ["contrato", "legal", "cliente", "XYZ"],
        "description": "Contrato de prestación de servicios con cliente XYZ renovado para 2025.",
        "metadata": {
            "author": "Departamento Legal",
            "created_date": "2024-12-15",
            "last_review": "2025-01-10",
            "next_review": "2025-12-31",
            "confidentiality": "Confidential",
            "page_count": 23,
            "contract_value": "$150,000 USD",
            "contract_period": "2025-01-01 to 2025-12-31",
        }
    },
    {
        "title": "Plan Estratégico 2025-2027",
        "filename": "plan_estrategico_2025_2027.pdf",
        "file_path": "/storage/demo/plan_estrategico_2025_2027.pdf",
        "file_size": 4194304,  # 4 MB
        "mime_type": "application/pdf",
        "version": "2.1",
        "status": "IN_REVIEW",
        "category": "Estrategia",
        "tags": ["estrategia", "planificación", "objetivos"],
        "description": "Plan estratégico corporativo con objetivos y KPIs para el período 2025-2027.",
        "metadata": {
            "author": "Dirección General",
            "created_date": "2024-10-01",
            "last_review": "2025-09-15",
            "next_review": "2025-11-15",
            "confidentiality": "Restricted",
            "page_count": 156,
        }
    },
]

DEMO_ANNOTATIONS = [
    # Anotaciones para Manual de Procedimientos
    {
        "document_index": 0,  # Manual de Procedimientos
        "page_number": 5,
        "annotation_type": "HIGHLIGHT",
        "color": "YELLOW",
        "position": {"x": 100, "y": 200, "width": 300, "height": 20},
        "content": "Proceso de aprobación revisado",
        "created_by_index": 1,  # revisor.demo
    },
    {
        "document_index": 0,
        "page_number": 12,
        "annotation_type": "STICKY_NOTE",
        "color": "ORANGE",
        "position": {"x": 450, "y": 350, "width": 40, "height": 40},
        "content": "IMPORTANTE: Actualizar este procedimiento según nueva normativa ISO 9001:2025",
        "created_by_index": 1,
    },
    {
        "document_index": 0,
        "page_number": 45,
        "annotation_type": "HIGHLIGHT",
        "color": "GREEN",
        "position": {"x": 80, "y": 500, "width": 400, "height": 18},
        "content": "Excelente práctica - replicar en otros departamentos",
        "created_by_index": 0,  # admin.demo
    },
    
    # Anotaciones para Política de Seguridad
    {
        "document_index": 1,  # Política de Seguridad
        "page_number": 3,
        "annotation_type": "REDACTION",
        "color": "BLACK",
        "position": {"x": 150, "y": 400, "width": 250, "height": 30},
        "content": "[INFORMACIÓN SENSIBLE REDACTADA]",
        "created_by_index": 0,
    },
    {
        "document_index": 1,
        "page_number": 8,
        "annotation_type": "STICKY_NOTE",
        "color": "RED",
        "position": {"x": 500, "y": 200, "width": 40, "height": 40},
        "content": "⚠️ URGENTE: Este apartado requiere revisión del CISO antes de aprobar",
        "created_by_index": 1,
    },
    {
        "document_index": 1,
        "page_number": 15,
        "annotation_type": "HIGHLIGHT",
        "color": "BLUE",
        "position": {"x": 120, "y": 300, "width": 350, "height": 22},
        "content": "Alineado con controles ISO 27001:2022",
        "created_by_index": 2,  # usuario.demo
    },
    
    # Anotaciones para Reporte Financiero
    {
        "document_index": 2,  # Reporte Financiero
        "page_number": 15,
        "annotation_type": "HIGHLIGHT",
        "color": "GREEN",
        "position": {"x": 200, "y": 450, "width": 280, "height": 20},
        "content": "Crecimiento del 15% respecto a Q2",
        "created_by_index": 0,
    },
    {
        "document_index": 2,
        "page_number": 23,
        "annotation_type": "STICKY_NOTE",
        "color": "PURPLE",
        "position": {"x": 400, "y": 300, "width": 40, "height": 40},
        "content": "💰 Excelentes resultados - Presentar en Junta Directiva",
        "created_by_index": 0,
    },
    {
        "document_index": 2,
        "page_number": 34,
        "annotation_type": "HIGHLIGHT",
        "color": "YELLOW",
        "position": {"x": 90, "y": 550, "width": 420, "height": 18},
        "content": "Variación significativa - solicitar análisis detallado",
        "created_by_index": 1,
    },
    
    # Anotaciones para Contrato
    {
        "document_index": 3,  # Contrato XYZ
        "page_number": 1,
        "annotation_type": "REDACTION",
        "color": "BLACK",
        "position": {"x": 300, "y": 600, "width": 200, "height": 25},
        "content": "[FIRMA REDACTADA]",
        "created_by_index": 0,
    },
    {
        "document_index": 3,
        "page_number": 7,
        "annotation_type": "HIGHLIGHT",
        "color": "YELLOW",
        "position": {"x": 100, "y": 250, "width": 350, "height": 20},
        "content": "Cláusula de renovación automática",
        "created_by_index": 2,
    },
    {
        "document_index": 3,
        "page_number": 12,
        "annotation_type": "STICKY_NOTE",
        "color": "BLUE",
        "position": {"x": 480, "y": 400, "width": 40, "height": 40},
        "content": "✓ Revisado por Legal - Aprobado sin cambios",
        "created_by_index": 1,
    },
    
    # Anotaciones para Plan Estratégico
    {
        "document_index": 4,  # Plan Estratégico
        "page_number": 10,
        "annotation_type": "HIGHLIGHT",
        "color": "GREEN",
        "position": {"x": 110, "y": 350, "width": 400, "height": 22},
        "content": "Objetivo clave: Transformación Digital",
        "created_by_index": 0,
    },
    {
        "document_index": 4,
        "page_number": 25,
        "annotation_type": "STICKY_NOTE",
        "color": "ORANGE",
        "position": {"x": 520, "y": 180, "width": 40, "height": 40},
        "content": "📊 KPI: Aumentar eficiencia operacional en 30%",
        "created_by_index": 0,
    },
    {
        "document_index": 4,
        "page_number": 50,
        "annotation_type": "HIGHLIGHT",
        "color": "PURPLE",
        "position": {"x": 130, "y": 480, "width": 320, "height": 20},
        "content": "Inversión en IA y automatización de procesos",
        "created_by_index": 2,
    },
]


def hash_password(password: str) -> str:
    """Hash password con bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_demo_users(session):
    """Crear usuarios de demostración"""
    print("📝 Creando usuarios de demostración...")
    
    users = []
    for user_data in DEMO_USERS:
        # Aquí deberías usar tu modelo User real
        # user = User(
        #     username=user_data["username"],
        #     email=user_data["email"],
        #     full_name=user_data["full_name"],
        #     role=user_data["role"],
        #     password_hash=hash_password(user_data["password"]),
        #     department=user_data["department"],
        #     is_active=True,
        #     created_at=datetime.utcnow(),
        # )
        # session.add(user)
        # users.append(user)
        
        print(f"   ✓ Usuario: {user_data['username']} ({user_data['role']})")
    
    session.commit()
    print(f"✅ {len(DEMO_USERS)} usuarios creados\n")
    return users


def create_demo_documents(session, users):
    """Crear documentos de demostración"""
    print("📄 Creando documentos de demostración...")
    
    documents = []
    for doc_data in DEMO_DOCUMENTS:
        # Aquí deberías usar tu modelo Document real
        # document = Document(
        #     title=doc_data["title"],
        #     filename=doc_data["filename"],
        #     file_path=doc_data["file_path"],
        #     file_size=doc_data["file_size"],
        #     mime_type=doc_data["mime_type"],
        #     version=doc_data["version"],
        #     status=doc_data["status"],
        #     category=doc_data["category"],
        #     tags=doc_data["tags"],
        #     description=doc_data["description"],
        #     metadata=doc_data["metadata"],
        #     uploaded_by_id=users[0].id,  # admin.demo
        #     created_at=datetime.utcnow() - timedelta(days=30),
        #     updated_at=datetime.utcnow() - timedelta(days=5),
        # )
        # session.add(document)
        # documents.append(document)
        
        print(f"   ✓ Documento: {doc_data['title']}")
    
    session.commit()
    print(f"✅ {len(DEMO_DOCUMENTS)} documentos creados\n")
    return documents


def create_demo_annotations(session, users, documents):
    """Crear anotaciones de demostración"""
    print("🎨 Creando anotaciones de demostración...")
    
    annotation_count = 0
    for annot_data in DEMO_ANNOTATIONS:
        document = documents[annot_data["document_index"]]
        user = users[annot_data["created_by_index"]]
        
        # Aquí deberías usar tu modelo Annotation real
        # annotation = Annotation(
        #     document_id=document.id,
        #     page_number=annot_data["page_number"],
        #     annotation_type=annot_data["annotation_type"],
        #     color=annot_data["color"],
        #     position=annot_data["position"],
        #     content=annot_data["content"],
        #     created_by_id=user.id,
        #     created_at=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
        # )
        # session.add(annotation)
        
        annotation_count += 1
        print(f"   ✓ Anotación: {annot_data['annotation_type']} en página {annot_data['page_number']} "
              f"de '{document.title[:40]}...'")
    
    session.commit()
    print(f"✅ {annotation_count} anotaciones creadas\n")


def main():
    """Función principal"""
    print("=" * 70)
    print("🎬 SEED DE DATOS DEMO - Sistema Documental Corporativo")
    print("=" * 70)
    print()
    
    # Nota: Este es un script de ejemplo
    # Necesitas descomentar y adaptar según tus modelos reales
    
    print("⚠️  NOTA: Este script es una plantilla.")
    print("    Debes descomentar y adaptar el código según tus modelos reales.\n")
    
    print("📋 Datos que se crearían:")
    print(f"   • {len(DEMO_USERS)} usuarios")
    print(f"   • {len(DEMO_DOCUMENTS)} documentos")
    print(f"   • {len(DEMO_ANNOTATIONS)} anotaciones")
    print()
    
    print("🔑 Credenciales de Demo:")
    print("   " + "-" * 66)
    for user in DEMO_USERS:
        print(f"   • Usuario: {user['username']:<20} | Password: {user['password']:<12} | Role: {user['role']}")
    print("   " + "-" * 66)
    print()
    
    # Descomentar para ejecutar realmente:
    # try:
    #     engine = create_engine(DATABASE_URL)
    #     SessionLocal = sessionmaker(bind=engine)
    #     session = SessionLocal()
    #     
    #     users = create_demo_users(session)
    #     documents = create_demo_documents(session, users)
    #     create_demo_annotations(session, users, documents)
    #     
    #     print("=" * 70)
    #     print("✅ SEED COMPLETADO EXITOSAMENTE")
    #     print("=" * 70)
    #     
    #     session.close()
    # except Exception as e:
    #     print(f"\n❌ Error al crear datos de demo: {e}")
    #     return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

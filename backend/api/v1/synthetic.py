"""
API Endpoints para Generación de Datos Sintéticos
Solo disponible para administradores en entornos no productivos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import os
from pathlib import Path

from core.config import settings
from core.auth import get_current_active_user, require_role
from models.database_models import User
# Switch to full synthetic data service for real PDF generation
from services.synthetic_data_service_full import synthetic_data_service
from core.logging_config import logger
from fastapi.responses import FileResponse


router = APIRouter(prefix="/synthetic", tags=["Synthetic Data"])


# ===== Schemas =====

class SyntheticDataRequest(BaseModel):
    """Request para generación de datos sintéticos"""
    total_documents: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Cantidad total de documentos a generar"
    )
    template_id: Optional[str] = Field(
        default="default",
        description="Template de distribución a usar"
    )
    custom_distribution: Optional[dict] = Field(
        default=None,
        description="Distribución personalizada por categoría"
    )
    auto_upload: bool = Field(
        default=True,
        description="Subir automáticamente a la aplicación"
    )


class SyntheticDataResponse(BaseModel):
    """Response de generación iniciada"""
    message: str
    task_id: str
    estimated_time_seconds: int
    total_documents: int
    status_endpoint: str


class GenerationStatus(BaseModel):
    """Estado de una tarea de generación"""
    task_id: str
    status: str
    progress: int
    documents_generated: int
    total_documents: int
    created_at: str
    output_path: Optional[str] = None
    error: Optional[str] = None
    documents_uploaded: Optional[int] = None


class TemplateInfo(BaseModel):
    """Información de un template de distribución"""
    id: str
    name: str
    description: str
    categories: dict


class SyntheticFileInfo(BaseModel):
    """Información de un archivo sintético generado"""
    filename: str
    category: str
    size: int
    created_at: str
    metadata: dict
    preview_text: str


class SyntheticFilesResponse(BaseModel):
    """Response con lista de archivos sintéticos"""
    task_id: str
    files: List[SyntheticFileInfo]
    total_files: int


# ===== Dependency: Verificar permisos =====

async def verify_synthetic_permissions(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verifica que el usuario tenga permisos para generar datos sintéticos
    
    Requiere:
    - Rol admin
    - Entorno no-producción
    """
    # Verificar rol admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can generate synthetic data"
        )
    
    # Bloquear en producción
    if settings.ENVIRONMENT == "production":
        logger.warning(
            f"User {current_user.id} attempted to generate synthetic data in production"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Synthetic data generation is not allowed in production environment"
        )
    
    return current_user


# ===== Endpoints =====

@router.post("/generate", response_model=SyntheticDataResponse)
async def generate_synthetic_data(
    request: SyntheticDataRequest,
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Genera documentos sintéticos
    
    **Restricciones:**
    - ⚠️ Solo administradores
    - ⚠️ Solo en entornos dev/staging
    - Máximo 500 documentos por request
    
    **Proceso:**
    1. Crea tarea de generación en background
    2. Genera documentos según template o distribución personalizada
    3. Opcionalmente sube documentos a la aplicación
    4. Retorna task_id para tracking de progreso
    
    **Templates disponibles:**
    - `default`: Distribución balanceada
    - `financial_heavy`: Enfoque en documentos financieros
    - `legal_compliance`: Foco en legal y compliance
    - `demo_mode`: Variado para demos
    """
    try:
        # Calcular distribución
        if request.custom_distribution:
            # Validar distribución personalizada
            total_in_dist = sum(request.custom_distribution.values())
            if total_in_dist != request.total_documents:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sum of custom distribution ({total_in_dist}) "
                           f"must equal total_documents ({request.total_documents})"
                )
            categories = request.custom_distribution
        else:
            # Usar template
            categories = synthetic_data_service.calculate_distribution(
                request.template_id,
                request.total_documents
            )
        
        # Iniciar generación
        task_id = await synthetic_data_service.generate_async(
            total_documents=request.total_documents,
            categories=categories,
            auto_upload=request.auto_upload,
            user_id=current_user.id
        )
        
        # Estimar tiempo (0.5 segundos por documento)
        estimated_time = int(request.total_documents * 0.5)
        
        logger.info(
            f"Synthetic data generation started: task_id={task_id}, "
            f"documents={request.total_documents}, user={current_user.id}"
        )
        
        return SyntheticDataResponse(
            message=f"Synthetic data generation started successfully",
            task_id=task_id,
            estimated_time_seconds=estimated_time,
            total_documents=request.total_documents,
            status_endpoint=f"/api/v1/synthetic/status/{task_id}"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting synthetic data generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start synthetic data generation"
        )


@router.get("/status/{task_id}", response_model=GenerationStatus)
async def get_generation_status(
    task_id: str,
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Obtiene el estado de una tarea de generación
    
    **Estados posibles:**
    - `pending`: Tarea creada, esperando ejecución
    - `running`: Generación en progreso
    - `completed`: Generación completada exitosamente
    - `failed`: Error durante la generación
    
    **Campos importantes:**
    - `progress`: Porcentaje de progreso (0-100)
    - `documents_generated`: Cantidad de documentos creados
    - `output_path`: Ruta donde se guardaron los archivos
    - `documents_uploaded`: Cantidad subida (si auto_upload=true)
    """
    status_data = await synthetic_data_service.get_task_status(task_id)
    
    if "error" in status_data and status_data.get("error") == "Task not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return GenerationStatus(**status_data)


@router.get("/tasks", response_model=List[GenerationStatus])
async def list_generation_tasks(
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Lista todas las tareas de generación del usuario actual
    
    Retorna tareas ordenadas por fecha de creación (más recientes primero)
    """
    tasks = await synthetic_data_service.list_tasks(user_id=current_user.id)
    
    return [GenerationStatus(**task) for task in tasks]


@router.delete("/tasks/{task_id}")
async def delete_generation_task(
    task_id: str,
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Elimina una tarea de generación y sus archivos asociados
    
    **Nota:** Solo puede eliminar tareas propias (mismo user_id)
    """
    # Verificar que la tarea existe
    status_data = await synthetic_data_service.get_task_status(task_id)
    
    if "error" in status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Verificar ownership (o ser admin)
    if status_data.get("user_id") != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )
    
    # Eliminar
    deleted = await synthetic_data_service.delete_task(task_id)
    
    if deleted:
        return {
            "message": f"Task {task_id} deleted successfully",
            "task_id": task_id
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )


@router.get("/templates", response_model=List[TemplateInfo])
async def list_templates(
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Lista templates de distribución disponibles
    
    Los templates definen cómo se distribuyen los documentos entre categorías:
    - Legal
    - Financial
    - HR
    - Technical
    - Marketing
    - Operations
    - Compliance
    - Multimedia
    """
    templates = synthetic_data_service.get_templates()
    
    # Convert dict to list of TemplateInfo
    template_list = []
    for template_id, template_data in templates.items():
        template_list.append({
            "id": template_id,
            "name": template_data["name"],
            "description": template_data["description"],
            "categories": template_data["categories"]
        })
    
    return template_list


@router.post("/preview-distribution")
async def preview_distribution(
    template_id: str,
    total_documents: int = 50,
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Preview de distribución sin generar documentos
    
    Útil para ver cómo se distribuirán los documentos antes de generarlos
    """
    if total_documents < 1 or total_documents > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="total_documents must be between 1 and 500"
        )
    
    distribution = synthetic_data_service.calculate_distribution(
        template_id, total_documents
    )
    
    return {
        "template_id": template_id,
        "total_documents": total_documents,
        "distribution": distribution,
        "percentages": {
            cat: f"{(count/total_documents)*100:.1f}%"
            for cat, count in distribution.items()
        }
    }


@router.get("/tasks/{task_id}/files", response_model=SyntheticFilesResponse)
async def get_task_files(
    task_id: str,
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Obtiene la lista de archivos sintéticos generados para una tarea
    
    Retorna información detallada de cada archivo incluyendo:
    - Filename y categoría
    - Tamaño del archivo
    - Metadata (entidades, chunks, risk_level)
    - Preview del contenido
    
    **Nota:** Lee directamente del filesystem si la tarea no está en memoria
    """
    # Intentar obtener desde el servicio primero
    status_data = await synthetic_data_service.get_task_status(task_id)
    
    # Si la tarea no está en memoria, buscar directamente en el filesystem
    output_path = None
    if "error" in status_data:
        # Construir path esperado basado en task_id
        expected_path = Path(f"/tmp/synthetic_documents/{task_id}")
        if expected_path.exists() and expected_path.is_dir():
            output_path = str(expected_path)
            logger.info(f"Task {task_id} not in memory, but found directory at {output_path}")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found and no directory exists"
            )
    else:
        # Verificar que está completada (solo si está en memoria)
        if status_data.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task {task_id} is not completed yet (status: {status_data.get('status')})"
            )
        
        # Obtener output_path
        output_path = status_data.get("output_path")
        if not output_path:
            # Fallback: intentar path esperado
            expected_path = Path(f"/tmp/synthetic_documents/{task_id}")
            if expected_path.exists():
                output_path = str(expected_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Output path not found for task {task_id}"
                )
    
    # Leer archivos del directorio
    try:
        output_dir = Path(output_path)
        if not output_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Output directory not found: {output_path}"
            )
        
        files_info = []
        
        # Buscar archivos PDF en el directorio
        for pdf_file in output_dir.glob("*.pdf"):
            # Leer metadata (buscar archivo .json con mismo nombre)
            metadata_file = pdf_file.with_suffix('.json')
            metadata = {
                "entities": [],
                "chunks": 0,
                "risk_level": "unknown"
            }
            
            if metadata_file.exists():
                import json
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        file_metadata = json.load(f)
                        metadata = {
                            "entities": file_metadata.get("entities", [])[:10],  # Primeras 10 entidades
                            "chunks": file_metadata.get("chunks", 0),
                            "risk_level": file_metadata.get("risk_level", "medium")
                        }
                except Exception as e:
                    logger.warning(f"Error reading metadata for {pdf_file}: {e}")
            
            # Extraer categoría del nombre del archivo
            category = "Unknown"
            filename_parts = pdf_file.stem.split('_')
            if len(filename_parts) >= 2:
                category = filename_parts[1].capitalize()
            
            # Leer preview del contenido (buscar archivo .txt)
            preview_text = "Preview no disponible"
            txt_file = pdf_file.with_suffix('.txt')
            if txt_file.exists():
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        preview_text = f.read()[:1000]  # Primeros 1000 caracteres
                except Exception as e:
                    logger.warning(f"Error reading text preview for {pdf_file}: {e}")
            
            # Información del archivo
            file_stat = pdf_file.stat()
            file_info = SyntheticFileInfo(
                filename=pdf_file.name,
                category=category,
                size=file_stat.st_size,
                created_at=status_data.get("created_at", ""),
                metadata=metadata,
                preview_text=preview_text
            )
            files_info.append(file_info)
        
        # Ordenar por nombre
        files_info.sort(key=lambda x: x.filename)
        
        return SyntheticFilesResponse(
            task_id=task_id,
            files=files_info,
            total_files=len(files_info)
        )
        
    except Exception as e:
        logger.error(f"Error reading task files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading task files: {str(e)}"
        )


@router.get("/tasks/{task_id}/files/{filename}")
async def download_file(
    task_id: str,
    filename: str,
    current_user: User = Depends(verify_synthetic_permissions)
):
    """
    Descarga un archivo generado específico
    
    El archivo debe pertenecer a una tarea completada.
    Solo se permiten descargar archivos PDF.
    
    **Seguridad:**
    - Valida que el archivo pertenezca a la tarea
    - Solo permite archivos .pdf
    - Previene path traversal attacks
    """
    # Validar filename (prevenir path traversal)
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    # Solo permitir PDFs
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files can be downloaded"
        )
    
    # Verificar que la tarea existe y está completada
    status_data = await synthetic_data_service.get_task_status(task_id)
    
    output_path = None
    if "error" not in status_data:
        # Verificar que está completada (solo si está en memoria)
        if status_data.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task {task_id} is not completed yet"
            )
        output_path = status_data.get("output_path")
    
    # Fallback: buscar directamente en filesystem
    if not output_path:
        expected_path = Path(f"/tmp/synthetic_documents/{task_id}")
        if expected_path.exists() and expected_path.is_dir():
            output_path = str(expected_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
    
    file_path = Path(output_path) / filename
    
    # Verificar que el archivo existe
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    # Retornar archivo
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename
    )

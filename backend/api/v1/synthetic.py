"""
API Endpoints para Generación de Datos Sintéticos
Solo disponible para administradores en entornos no productivos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.core.auth import get_current_active_user, require_role
from backend.models.database_models import User
from backend.services.synthetic_data_service import synthetic_data_service
from backend.core.logging_config import logger


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
    templates = synthetic_data_service.get_available_templates()
    
    return [TemplateInfo(**template) for template in templates]


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

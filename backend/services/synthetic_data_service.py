"""
Servicio de Generación de Datos Sintéticos
Permite generar documentos de prueba desde la API
"""
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json
import tempfile

from core.logging_config import logger
from core.config import settings


class SyntheticDataService:
    """Servicio para generación de datos sintéticos"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}  # Almacena estado de tareas
        self.output_base_dir = Path(tempfile.gettempdir()) / "financia_synthetic"
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_async(
        self,
        total_documents: int = 50,
        categories: Optional[Dict[str, int]] = None,
        auto_upload: bool = False,
        user_id: Optional[int] = None
    ) -> str:
        """
        Inicia generación asíncrona de documentos
        
        Args:
            total_documents: Cantidad total de documentos a generar
            categories: Distribución personalizada por categoría
            auto_upload: Si True, sube automáticamente a la aplicación
            user_id: ID del usuario que solicita la generación
            
        Returns:
            str: ID de la tarea para tracking
        """
        task_id = str(uuid.uuid4())
        
        # Crear entrada de tarea
        self.tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "progress": 0,
            "documents_generated": 0,
            "total_documents": total_documents,
            "categories": categories,
            "auto_upload": auto_upload,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "output_path": None,
            "error": None
        }
        
        # Ejecutar en background
        asyncio.create_task(self._generate_task(task_id, total_documents, categories, auto_upload))
        
        logger.info(f"Synthetic data generation task {task_id} created by user {user_id}")
        
        return task_id
    
    async def _generate_task(
        self,
        task_id: str,
        total_documents: int,
        categories: Optional[Dict[str, int]],
        auto_upload: bool
    ):
        """Tarea de generación en background"""
        try:
            # Actualizar estado
            self.tasks[task_id]["status"] = "running"
            self.tasks[task_id]["started_at"] = datetime.utcnow().isoformat()
            
            # Crear directorio de salida
            output_dir = self.output_base_dir / task_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Importar generador (lazy import para evitar cargar dependencias pesadas)
            from scripts.generate_synthetic_data import SyntheticDataGenerator
            
            # Crear instancia del generador
            generator = SyntheticDataGenerator(output_dir=str(output_dir))
            
            # Configurar distribución si se proporciona
            if categories:
                # Validar que la suma coincida con total_documents
                if sum(categories.values()) != total_documents:
                    raise ValueError(
                        f"Sum of categories ({sum(categories.values())}) "
                        f"must equal total_documents ({total_documents})"
                    )
            
            # Generar documentos con callback de progreso
            await self._generate_with_progress(
                generator, task_id, total_documents, categories
            )
            
            # Si auto_upload, subir documentos
            if auto_upload:
                await self._upload_documents(task_id, output_dir)
            
            # Actualizar estado final
            self.tasks[task_id].update({
                "status": "completed",
                "progress": 100,
                "output_path": str(output_dir),
                "completed_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            self.tasks[task_id].update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            })
    
    async def _generate_with_progress(
        self,
        generator,
        task_id: str,
        total_documents: int,
        categories: Optional[Dict[str, int]]
    ):
        """Genera documentos con actualización de progreso"""
        
        # Distribución por defecto o personalizada
        if categories:
            distribution = categories
        else:
            # Distribución por defecto proporcional
            distribution = {
                "legal": int(total_documents * 0.15),
                "financial": int(total_documents * 0.175),
                "hr": int(total_documents * 0.125),
                "technical": int(total_documents * 0.125),
                "marketing": int(total_documents * 0.10),
                "operations": int(total_documents * 0.10),
                "compliance": int(total_documents * 0.125),
                "multimedia": int(total_documents * 0.10)
            }
            
            # Ajustar para que sume exactamente total_documents
            current_sum = sum(distribution.values())
            if current_sum < total_documents:
                distribution["financial"] += (total_documents - current_sum)
        
        generated = 0
        
        # Generar por categoría
        for category, count in distribution.items():
            logger.info(f"Task {task_id}: Generating {count} {category} documents")
            
            for i in range(count):
                # Generar documento según categoría
                try:
                    if category == "legal":
                        generator.generate_contract(i)
                    elif category == "financial":
                        if i % 2 == 0:
                            generator.generate_invoice(i)
                        else:
                            generator.generate_budget(i)
                    elif category == "hr":
                        if i % 2 == 0:
                            generator.generate_payroll(i)
                        else:
                            generator.generate_employment_contract(i)
                    elif category == "technical":
                        generator.generate_technical_spec(i)
                    elif category == "marketing":
                        generator.generate_marketing_report(i)
                    elif category == "operations":
                        generator.generate_operational_doc(i)
                    elif category == "compliance":
                        generator.generate_compliance_policy(i)
                    elif category == "multimedia":
                        if i % 2 == 0:
                            generator.generate_scanned_document(i)
                        else:
                            generator.generate_infographic(i)
                    
                    generated += 1
                    
                    # Actualizar progreso
                    progress = int((generated / total_documents) * 100)
                    self.tasks[task_id].update({
                        "progress": progress,
                        "documents_generated": generated
                    })
                    
                    # Pequeña pausa para no saturar
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    logger.error(f"Error generating document {i} in {category}: {e}")
                    continue
        
        # Generar manifest
        generator._generate_manifest(generated)
        
        logger.info(f"Task {task_id}: Generated {generated} documents")
    
    async def _upload_documents(self, task_id: str, output_dir: Path):
        """Sube documentos generados a la aplicación"""
        try:
            from services.ingest_service import ingest_service
            from core.database import AsyncSessionLocal
            
            logger.info(f"Task {task_id}: Starting auto-upload")
            
            # Obtener todos los archivos generados
            files = []
            for category_dir in output_dir.iterdir():
                if category_dir.is_dir():
                    files.extend(list(category_dir.glob("*")))
            
            uploaded = 0
            async with AsyncSessionLocal() as db:
                for file_path in files:
                    try:
                        # Leer archivo
                        with open(file_path, "rb") as f:
                            file_content = f.read()
                        
                        # Subir usando ingest_service
                        await ingest_service.upload_document(
                            file_content=file_content,
                            filename=file_path.name,
                            content_type=self._get_content_type(file_path.suffix),
                            user_id=self.tasks[task_id].get("user_id"),
                            db=db
                        )
                        
                        uploaded += 1
                        
                    except Exception as e:
                        logger.error(f"Error uploading {file_path.name}: {e}")
                        continue
            
            logger.info(f"Task {task_id}: Uploaded {uploaded}/{len(files)} documents")
            self.tasks[task_id]["documents_uploaded"] = uploaded
            
        except Exception as e:
            logger.error(f"Task {task_id}: Upload failed: {e}", exc_info=True)
            self.tasks[task_id]["upload_error"] = str(e)
    
    def _get_content_type(self, extension: str) -> str:
        """Obtiene content type según extensión"""
        content_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg"
        }
        return content_types.get(extension.lower(), "application/octet-stream")
    
    async def get_task_status(self, task_id: str) -> Dict:
        """
        Obtiene estado de una tarea de generación
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Dict con estado de la tarea
        """
        if task_id not in self.tasks:
            return {
                "error": "Task not found",
                "task_id": task_id
            }
        
        return self.tasks[task_id]
    
    async def list_tasks(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Lista todas las tareas de generación
        
        Args:
            user_id: Filtrar por usuario (opcional)
            
        Returns:
            Lista de tareas
        """
        tasks = list(self.tasks.values())
        
        if user_id:
            tasks = [t for t in tasks if t.get("user_id") == user_id]
        
        # Ordenar por fecha de creación (más recientes primero)
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return tasks
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Elimina una tarea y sus archivos
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            bool: True si se eliminó correctamente
        """
        if task_id not in self.tasks:
            return False
        
        # Eliminar archivos si existen
        output_path = self.tasks[task_id].get("output_path")
        if output_path:
            try:
                import shutil
                shutil.rmtree(output_path, ignore_errors=True)
            except Exception as e:
                logger.error(f"Error deleting output directory: {e}")
        
        # Eliminar tarea
        del self.tasks[task_id]
        
        logger.info(f"Task {task_id} deleted")
        return True
    
    def get_available_templates(self) -> List[Dict]:
        """
        Obtiene lista de templates disponibles
        
        Returns:
            Lista de templates con descripción
        """
        return [
            {
                "id": "default",
                "name": "Distribución Balanceada",
                "description": "Distribución equilibrada entre todas las categorías",
                "categories": {
                    "legal": "15%",
                    "financial": "17.5%",
                    "hr": "12.5%",
                    "technical": "12.5%",
                    "marketing": "10%",
                    "operations": "10%",
                    "compliance": "12.5%",
                    "multimedia": "10%"
                }
            },
            {
                "id": "financial_heavy",
                "name": "Enfoque Financiero",
                "description": "Mayor proporción de documentos financieros",
                "categories": {
                    "legal": "10%",
                    "financial": "40%",
                    "hr": "10%",
                    "technical": "5%",
                    "marketing": "5%",
                    "operations": "10%",
                    "compliance": "15%",
                    "multimedia": "5%"
                }
            },
            {
                "id": "legal_compliance",
                "name": "Legal & Compliance",
                "description": "Foco en documentos legales y de cumplimiento",
                "categories": {
                    "legal": "30%",
                    "financial": "15%",
                    "hr": "10%",
                    "technical": "5%",
                    "marketing": "5%",
                    "operations": "10%",
                    "compliance": "25%",
                    "multimedia": "0%"
                }
            },
            {
                "id": "demo_mode",
                "name": "Modo Demo",
                "description": "Selección variada para demostraciones",
                "categories": {
                    "legal": "20%",
                    "financial": "20%",
                    "hr": "15%",
                    "technical": "15%",
                    "marketing": "10%",
                    "operations": "10%",
                    "compliance": "10%",
                    "multimedia": "0%"
                }
            }
        ]
    
    def calculate_distribution(
        self,
        template_id: str,
        total_documents: int
    ) -> Dict[str, int]:
        """
        Calcula distribución de documentos según template
        
        Args:
            template_id: ID del template
            total_documents: Cantidad total de documentos
            
        Returns:
            Dict con cantidad por categoría
        """
        templates = {t["id"]: t for t in self.get_available_templates()}
        
        if template_id not in templates:
            template_id = "default"
        
        template = templates[template_id]
        distribution = {}
        
        for category, percentage in template["categories"].items():
            # Convertir porcentaje a cantidad
            pct = float(percentage.rstrip("%")) / 100
            count = int(total_documents * pct)
            distribution[category] = count
        
        # Ajustar para que sume exactamente total_documents
        current_sum = sum(distribution.values())
        if current_sum < total_documents:
            # Añadir diferencia a la categoría con más documentos
            max_category = max(distribution, key=distribution.get)
            distribution[max_category] += (total_documents - current_sum)
        elif current_sum > total_documents:
            # Restar diferencia de la categoría con más documentos
            max_category = max(distribution, key=distribution.get)
            distribution[max_category] -= (current_sum - total_documents)
        
        return distribution


# Singleton
synthetic_data_service = SyntheticDataService()

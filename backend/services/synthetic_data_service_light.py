"""
Lightweight Synthetic Data Service Instance
"""

class LightweightSyntheticDataService:
    """Lightweight synthetic data service for basic functionality"""
    
    def __init__(self):
        self.tasks = {}
    
    def calculate_distribution(self, template_id: str, total_documents: int) -> dict:
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
    
    async def generate_async(self, total_documents=50, categories=None, auto_upload=False, user_id=None):
        """Mock async generation"""
        import uuid
        from datetime import datetime
        
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "id": task_id,
            "status": "completed",  # Mock as completed immediately
            "progress": 100,
            "total_documents": total_documents,
            "generated_documents": total_documents,
            "user_id": user_id,
            "categories": categories or {},
            "created_at": datetime.utcnow().isoformat()
        }
        return task_id
    
    async def get_task_status(self, task_id: str):
        """Get task status"""
        from datetime import datetime
        
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        
        # Ensure all required fields are present
        return {
            "task_id": task_id,
            "status": task.get("status", "pending"),
            "progress": task.get("progress", 0),
            "documents_generated": task.get("generated_documents", 0),
            "total_documents": task.get("total_documents", 0),
            "created_at": task.get("created_at", datetime.utcnow().isoformat()),
            "output_path": task.get("output_path"),
            "documents_uploaded": task.get("documents_uploaded")
        }
    
    async def list_tasks(self, user_id: str = None):
        """List all tasks for a user"""
        from datetime import datetime
        
        tasks = []
        for task_id, task in self.tasks.items():
            if user_id is None or task.get("user_id") == user_id:
                tasks.append({
                    "task_id": task_id,
                    "status": task.get("status", "pending"),
                    "progress": task.get("progress", 0),
                    "documents_generated": task.get("generated_documents", 0),
                    "total_documents": task.get("total_documents", 0),
                    "created_at": datetime.utcnow().isoformat(),
                    "output_path": task.get("output_path"),
                    "documents_uploaded": task.get("documents_uploaded")
                })
        return tasks
    
    def get_templates(self):
        """Get available templates with their distributions"""
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
    
    def get_available_templates(self):
        """Alias for get_templates - for API compatibility"""
        return self.get_templates()

# Create service instance
synthetic_data_service = LightweightSyntheticDataService()

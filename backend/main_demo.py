"""
Backend Simplificado para Demo - FinancIA 2030
Proporciona endpoints mock para testing del frontend
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import uvicorn

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="FinancIA 2030 - Demo API",
    description="Backend simplificado para demostración",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8000",
        "https://glowing-system-57vgpqp6qj63p4jx-3000.app.github.dev",
        "https://glowing-system-57vgpqp6qj63p4jx-8000.app.github.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# ============================================================================
# MODELOS
# ============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class DocumentSummary(BaseModel):
    id: str
    filename: str
    type: str
    uploaded_at: str
    status: str

# ============================================================================
# BASE DE DATOS MOCK
# ============================================================================

# Password para todos: Demo2025!
DEMO_USERS_DB = {
    "admin.demo": {
        "username": "admin.demo",
        "full_name": "Administrador Demo",
        "email": "admin@demo.documental.com",
        "role": "ADMIN",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "revisor.demo": {
        "username": "revisor.demo",
        "full_name": "Revisor Demo",
        "email": "revisor@demo.documental.com",
        "role": "REVIEWER",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "usuario.demo": {
        "username": "usuario.demo",
        "full_name": "Usuario Demo",
        "email": "usuario@demo.documental.com",
        "role": "USER",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "lectura.demo": {
        "username": "lectura.demo",
        "full_name": "Lector Demo",
        "email": "lectura@demo.documental.com",
        "role": "VIEWER",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
}

DEMO_DOCUMENTS = [
    {
        "id": "doc-001",
        "filename": "Contrato_Suministro_2024.pdf",
        "type": "LEGAL_CONTRACT",
        "uploaded_at": "2024-12-15T10:30:00Z",
        "status": "PROCESSED",
        "owner": "admin.demo",
    },
    {
        "id": "doc-002",
        "filename": "Estados_Financieros_Q4.pdf",
        "type": "FINANCIAL_STATEMENT",
        "uploaded_at": "2024-12-10T14:20:00Z",
        "status": "PROCESSED",
        "owner": "usuario.demo",
    },
    {
        "id": "doc-003",
        "filename": "Informe_Riesgos_2024.pdf",
        "type": "RISK_REPORT",
        "uploaded_at": "2024-12-01T09:15:00Z",
        "status": "PROCESSED",
        "owner": "revisor.demo",
    },
]

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def verify_password(plain_password, hashed_password):
    # Para demo, simplemente verificamos que la password sea "Demo2025!"
    return plain_password == "Demo2025!"

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    if username in DEMO_USERS_DB:
        user_dict = DEMO_USERS_DB[username]
        return UserInDB(**user_dict)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    # Simplificado para demo: todos los usuarios tienen password "Demo2025!"
    if password != "Demo2025!":
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "FinancIA 2030 Demo API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Auth Endpoints
@app.post("/api/v1/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Document Endpoints
@app.get("/api/v1/documents", response_model=List[DocumentSummary])
async def list_documents(current_user: User = Depends(get_current_active_user)):
    """Lista todos los documentos disponibles"""
    return [
        DocumentSummary(
            id=doc["id"],
            filename=doc["filename"],
            type=doc["type"],
            uploaded_at=doc["uploaded_at"],
            status=doc["status"]
        )
        for doc in DEMO_DOCUMENTS
    ]

@app.get("/api/v1/documents/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene detalles de un documento específico"""
    for doc in DEMO_DOCUMENTS:
        if doc["id"] == document_id:
            return {
                **doc,
                "size": 1024000,
                "pages": 12,
                "language": "es",
                "classification": doc["type"],
                "confidence": 0.95,
            }
    raise HTTPException(status_code=404, detail="Document not found")

# Search Endpoint
@app.post("/api/v1/search")
async def search_documents(
    query: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Búsqueda semántica de documentos"""
    return {
        "query": query.get("query", ""),
        "results": [
            {
                "document_id": doc["id"],
                "filename": doc["filename"],
                "score": 0.85,
                "snippet": f"Fragmento relevante de {doc['filename']}...",
                "page": 3
            }
            for doc in DEMO_DOCUMENTS[:2]
        ],
        "total": 2,
        "took_ms": 45
    }

# RAG Endpoint
@app.post("/api/v1/rag/query")
async def rag_query(
    query: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Consulta RAG con contexto documental"""
    return {
        "query": query.get("question", ""),
        "answer": "Esta es una respuesta de demostración generada por el sistema RAG. "
                  "En producción, esto sería generado por un LLM con contexto de documentos reales.",
        "sources": [
            {
                "document_id": "doc-001",
                "filename": "Contrato_Suministro_2024.pdf",
                "page": 5,
                "relevance": 0.92
            }
        ],
        "confidence": 0.88
    }

# Dashboard Stats
@app.get("/api/v1/stats/dashboard")
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Estadísticas para el dashboard"""
    return {
        "total_documents": len(DEMO_DOCUMENTS),
        "processed_today": 5,
        "pending_review": 2,
        "active_users": 4,
        "storage_used_gb": 12.5,
        "storage_total_gb": 100,
        "total_chunks": 1250,
        "total_entities": 342,
        "documents_by_category": {
            "Contratos": 1,
            "Financiero": 1,
            "Riesgos": 1
        },
        "risk_distribution": {
            "low": 1,
            "medium": 1,
            "high": 1,
            "critical": 0
        },
        "compliance_summary": {
            "compliant": 2,
            "non_compliant": 1,
            "pending": 0
        },
        "recent_uploads": [
            {
                "id": "doc-001",
                "filename": "Contrato_Suministro_2024.pdf",
                "category": "Contratos",
                "uploaded_at": datetime.utcnow().isoformat()
            },
            {
                "id": "doc-002",
                "filename": "Estados_Financieros_Q4.pdf",
                "category": "Financiero",
                "uploaded_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            },
            {
                "id": "doc-003",
                "filename": "Informe_Riesgos_2024.pdf",
                "category": "Riesgos",
                "uploaded_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
            }
        ],
        "recent_activity": [
            {
                "action": "document_uploaded",
                "user": "admin.demo",
                "timestamp": datetime.utcnow().isoformat(),
                "details": "Contrato_Suministro_2024.pdf"
            },
            {
                "action": "document_reviewed",
                "user": "revisor.demo",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "details": "Estados_Financieros_Q4.pdf"
            },
            {
                "action": "document_validated",
                "user": "admin.demo",
                "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                "details": "Informe_Riesgos_2024.pdf"
            }
        ]
    }

# Dashboard Stats - Ruta alternativa para compatibilidad
@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats_alt(current_user: User = Depends(get_current_active_user)):
    """Estadísticas para el dashboard (ruta alternativa)"""
    return {
        "total_documents": len(DEMO_DOCUMENTS),
        "processed_today": 5,
        "pending_review": 2,
        "active_users": 4,
        "storage_used_gb": 12.5,
        "storage_total_gb": 100,
        "total_chunks": 1250,
        "total_entities": 342,
        "documents_by_category": {
            "Contratos": 1,
            "Financiero": 1,
            "Riesgos": 1
        },
        "risk_distribution": {
            "low": 1,
            "medium": 1,
            "high": 1,
            "critical": 0
        },
        "compliance_summary": {
            "compliant": 2,
            "non_compliant": 1,
            "pending": 0
        },
        "recent_uploads": [
            {
                "id": "doc-001",
                "filename": "Contrato_Suministro_2024.pdf",
                "category": "Contratos",
                "uploaded_at": datetime.utcnow().isoformat()
            },
            {
                "id": "doc-002",
                "filename": "Estados_Financieros_Q4.pdf",
                "category": "Financiero",
                "uploaded_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            },
            {
                "id": "doc-003",
                "filename": "Informe_Riesgos_2024.pdf",
                "category": "Riesgos",
                "uploaded_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
            }
        ],
        "recent_activity": [
            {
                "action": "document_uploaded",
                "user": "admin.demo",
                "timestamp": datetime.utcnow().isoformat(),
                "details": "Contrato_Suministro_2024.pdf"
            },
            {
                "action": "document_reviewed",
                "user": "revisor.demo",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "details": "Estados_Financieros_Q4.pdf"
            },
            {
                "action": "document_validated",
                "user": "admin.demo",
                "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                "details": "Informe_Riesgos_2024.pdf"
            }
        ]
    }

# ============================================================================
# ONTOLOGY ENDPOINTS
# ============================================================================

@app.get("/api/v1/ontology/hierarchy")
async def get_ontology_hierarchy(current_user: User = Depends(get_current_active_user)):
    """Obtener jerarquía de la ontología"""
    return {
        "nodes": [
            {
                "id": "root",
                "label": "Sistema Documental",
                "type": "root",
                "children": ["contracts", "financial", "risks"]
            },
            {
                "id": "contracts",
                "label": "Contratos",
                "type": "category",
                "parent": "root",
                "children": ["contract_supply", "contract_service"]
            },
            {
                "id": "contract_supply",
                "label": "Contrato de Suministro",
                "type": "subcategory",
                "parent": "contracts",
                "children": []
            },
            {
                "id": "contract_service",
                "label": "Contrato de Servicios",
                "type": "subcategory",
                "parent": "contracts",
                "children": []
            },
            {
                "id": "financial",
                "label": "Documentos Financieros",
                "type": "category",
                "parent": "root",
                "children": ["financial_statements", "financial_reports"]
            },
            {
                "id": "financial_statements",
                "label": "Estados Financieros",
                "type": "subcategory",
                "parent": "financial",
                "children": []
            },
            {
                "id": "financial_reports",
                "label": "Informes Financieros",
                "type": "subcategory",
                "parent": "financial",
                "children": []
            },
            {
                "id": "risks",
                "label": "Gestión de Riesgos",
                "type": "category",
                "parent": "root",
                "children": ["risk_assessment", "risk_mitigation"]
            },
            {
                "id": "risk_assessment",
                "label": "Evaluación de Riesgos",
                "type": "subcategory",
                "parent": "risks",
                "children": []
            },
            {
                "id": "risk_mitigation",
                "label": "Mitigación de Riesgos",
                "type": "subcategory",
                "parent": "risks",
                "children": []
            }
        ],
        "relationships": [
            {"source": "root", "target": "contracts", "type": "contains"},
            {"source": "root", "target": "financial", "type": "contains"},
            {"source": "root", "target": "risks", "type": "contains"},
            {"source": "contracts", "target": "contract_supply", "type": "contains"},
            {"source": "contracts", "target": "contract_service", "type": "contains"},
            {"source": "financial", "target": "financial_statements", "type": "contains"},
            {"source": "financial", "target": "financial_reports", "type": "contains"},
            {"source": "risks", "target": "risk_assessment", "type": "contains"},
            {"source": "risks", "target": "risk_mitigation", "type": "contains"}
        ]
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🚀 Iniciando FinancIA 2030 Demo Backend...")
    print("📝 Credenciales de demo:")
    print("   - admin.demo / Demo2025!")
    print("   - revisor.demo / Demo2025!")
    print("   - usuario.demo / Demo2025!")
    print("   - lectura.demo / Demo2025!")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")
    
    uvicorn.run(
        "main_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

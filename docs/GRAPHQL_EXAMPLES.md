# GraphQL API Examples

Ejemplos completos de uso del GraphQL API de FinancIA.

## 🚀 Acceso al GraphQL Playground

```
http://localhost:8000/api/graphql/
```

El Playground incluye:
- 📝 Editor de queries con autocompletado
- 📖 Documentación interactiva del schema
- 🔍 Explorador de tipos
- ⚡ Ejecución de queries y mutations

---

## 📚 Queries

### 1. Obtener un documento por ID

```graphql
query GetDocument {
  document(id: "doc-123") {
    id
    filename
    status
    mimeType
    size
    pageCount
    uploadedAt
    uploader {
      email
      fullName
    }
    entities {
      type
      text
      confidence
    }
  }
}
```

### 2. Listar documentos con filtros

```graphql
query ListDocuments {
  documents(
    filter: {
      status: COMPLETED
      minConfidence: 0.8
      uploadedAfter: "2024-01-01T00:00:00Z"
    }
    limit: 10
    orderBy: "uploaded_at"
    orderDesc: true
  ) {
    id
    filename
    status
    confidenceScore
    uploadedAt
  }
}
```

### 3. Paginación con cursores

```graphql
query PaginatedDocuments {
  documentsPaginated(
    first: 20
    after: "cursor-xyz"
    filter: { status: COMPLETED }
  ) {
    edges {
      cursor
      node {
        id
        filename
        status
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

### 4. Búsqueda semántica

```graphql
query SearchDocuments {
  search(
    query: "contratos de proveedores 2024"
    limit: 5
    minScore: 0.7
  ) {
    score
    highlights
    document {
      id
      filename
      uploadedAt
    }
    matchedChunks {
      content
      pageNumber
    }
  }
}
```

### 5. RAG Query (Pregunta sobre documentos)

```graphql
query AskQuestion {
  ragQuery(
    question: "¿Cuál es el monto total de los contratos firmados en 2024?"
    maxChunks: 5
    temperature: 0.7
  ) {
    answer
    confidence
    sources {
      id
      filename
      url
    }
    chunksUsed {
      content
      pageNumber
      documentId
    }
    metadata
  }
}
```

### 6. Obtener entidades con filtros

```graphql
query GetEntities {
  entities(
    documentId: "doc-123"
    type: MONEY
    limit: 50
  ) {
    id
    type
    text
    confidence
    pageNumber
    startOffset
    endOffset
  }
}
```

### 7. Obtener anotaciones

```graphql
query GetAnnotations {
  annotations(documentId: "doc-123") {
    id
    type
    content
    pageNumber
    position
    color
    createdAt
    user {
      email
      fullName
    }
  }
}
```

### 8. Usuario actual

```graphql
query GetCurrentUser {
  me {
    id
    email
    fullName
    role
    createdAt
  }
}
```

### 9. Query compleja con múltiples niveles

```graphql
query ComplexDocumentQuery {
  document(id: "doc-123") {
    id
    filename
    status
    
    # Entidades extraídas
    entities(type: CONTRACT) {
      text
      confidence
      pageNumber
    }
    
    # Chunks para RAG
    chunks(limit: 5) {
      content
      pageNumber
      chunkIndex
    }
    
    # Anotaciones de usuarios
    annotations(type: HIGHLIGHT) {
      content
      position
      user {
        email
      }
    }
    
    # Usuario que subió
    uploader {
      email
      fullName
    }
    
    # Validaciones
    validationResults {
      field
      rule
      passed
      message
      severity
    }
  }
}
```

---

## ✏️ Mutations

### 1. Upload de documento

```graphql
mutation UploadDocument($file: Upload!, $metadata: JSON) {
  uploadDocument(file: $file, metadata: $metadata) {
    success
    message
    document {
      id
      filename
      status
      uploadedAt
    }
  }
}

# Variables:
{
  "file": null,  # Se envía como multipart/form-data
  "metadata": {
    "category": "contracts",
    "department": "finance",
    "year": 2024
  }
}
```

**Ejemplo con curl:**

```bash
curl -X POST http://localhost:8000/api/graphql/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F operations='{"query": "mutation($file: Upload!) { uploadDocument(file: $file) { success document { id filename } } }", "variables": {"file": null}}' \
  -F map='{"0": ["variables.file"]}' \
  -F 0=@/path/to/document.pdf
```

### 2. Eliminar documento

```graphql
mutation DeleteDocument {
  deleteDocument(id: "doc-123") {
    success
    message
  }
}
```

### 3. Añadir anotación

```graphql
mutation AddAnnotation {
  addAnnotation(input: {
    documentId: "doc-123"
    type: HIGHLIGHT
    content: "Revisar esta cláusula"
    pageNumber: 3
    position: {
      x: 100
      y: 200
      width: 300
      height: 50
    }
    color: "#FFEB3B"
  }) {
    success
    message
    annotation {
      id
      type
      content
      createdAt
    }
  }
}
```

### 4. Actualizar anotación

```graphql
mutation UpdateAnnotation {
  updateAnnotation(
    id: "annot-456"
    input: {
      content: "Contenido actualizado"
      color: "#4CAF50"
    }
  ) {
    success
    message
    annotation {
      id
      content
      color
      updatedAt
    }
  }
}
```

### 5. Eliminar anotación

```graphql
mutation DeleteAnnotation {
  deleteAnnotation(id: "annot-456") {
    success
    message
  }
}
```

---

## 🔄 Ejemplos con Variables

### Query con variables

```graphql
query GetDocumentsByStatus($status: DocumentStatus!, $limit: Int) {
  documents(
    filter: { status: $status }
    limit: $limit
  ) {
    id
    filename
    status
  }
}
```

Variables:
```json
{
  "status": "COMPLETED",
  "limit": 20
}
```

### Mutation con variables

```graphql
mutation CreateAnnotation($input: AnnotationInput!) {
  addAnnotation(input: $input) {
    success
    annotation {
      id
      type
    }
  }
}
```

Variables:
```json
{
  "input": {
    "documentId": "doc-123",
    "type": "STICKY_NOTE",
    "content": "Importante!",
    "pageNumber": 1,
    "position": {"x": 50, "y": 100, "width": 200, "height": 100}
  }
}
```

---

## 🎯 Fragments (Reutilización)

```graphql
fragment DocumentBasic on Document {
  id
  filename
  status
  uploadedAt
}

fragment DocumentFull on Document {
  ...DocumentBasic
  mimeType
  size
  pageCount
  uploader {
    email
    fullName
  }
}

query GetDocuments {
  documents(limit: 5) {
    ...DocumentFull
  }
}

query GetDocument($id: ID!) {
  document(id: $id) {
    ...DocumentFull
    entities {
      type
      text
    }
  }
}
```

---

## 🔐 Autenticación

Todas las requests deben incluir el header de autenticación:

```bash
curl -X POST http://localhost:8000/api/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "{ me { email } }"}'
```

En GraphQL Playground, configurar HTTP Headers:

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

---

## 📊 Batching con DataLoaders

El API utiliza DataLoaders para optimizar queries N+1:

```graphql
# Esta query solo hace 3 queries a la DB (no 1+N):
# 1. Obtener documentos
# 2. Batch load de usuarios
# 3. Batch load de entidades
query EfficientQuery {
  documents(limit: 10) {
    id
    filename
    uploader {      # DataLoader batch load
      email
    }
    entities {      # DataLoader batch load
      type
      text
    }
  }
}
```

---

## 🚨 Manejo de Errores

### Error de autenticación

```json
{
  "data": {
    "uploadDocument": {
      "success": false,
      "message": "Authentication required",
      "document": null
    }
  }
}
```

### Error de validación

```json
{
  "errors": [
    {
      "message": "Field 'document' argument 'id' of type 'ID!' is required but not provided.",
      "locations": [{"line": 2, "column": 3}]
    }
  ]
}
```

### Error de permisos

```json
{
  "data": {
    "deleteDocument": {
      "success": false,
      "message": "You don't have permission to delete this document"
    }
  }
}
```

---

## 🎨 Introspection Query

Obtener todo el schema:

```graphql
query IntrospectionQuery {
  __schema {
    types {
      name
      kind
      description
      fields {
        name
        type {
          name
          kind
        }
      }
    }
  }
}
```

---

## 📱 Ejemplo Frontend (React + Apollo)

```typescript
import { gql, useQuery, useMutation } from '@apollo/client';

// Query
const GET_DOCUMENTS = gql`
  query GetDocuments($filter: DocumentFilter) {
    documents(filter: $filter, limit: 20) {
      id
      filename
      status
      uploadedAt
    }
  }
`;

function DocumentList() {
  const { loading, error, data } = useQuery(GET_DOCUMENTS, {
    variables: { filter: { status: 'COMPLETED' } }
  });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <ul>
      {data.documents.map(doc => (
        <li key={doc.id}>{doc.filename}</li>
      ))}
    </ul>
  );
}

// Mutation
const ADD_ANNOTATION = gql`
  mutation AddAnnotation($input: AnnotationInput!) {
    addAnnotation(input: $input) {
      success
      message
      annotation {
        id
      }
    }
  }
`;

function AddAnnotationButton() {
  const [addAnnotation] = useMutation(ADD_ANNOTATION);

  const handleClick = async () => {
    const result = await addAnnotation({
      variables: {
        input: {
          documentId: "doc-123",
          type: "HIGHLIGHT",
          pageNumber: 1,
          position: { x: 100, y: 200, width: 300, height: 50 }
        }
      }
    });
    
    console.log(result.data.addAnnotation);
  };

  return <button onClick={handleClick}>Add Annotation</button>;
}
```

---

## 🧪 Testing

### Pytest example

```python
import pytest
from strawberry.test import BaseGraphQLTestClient

@pytest.mark.asyncio
async def test_get_document():
    query = """
        query GetDocument($id: ID!) {
            document(id: $id) {
                id
                filename
                status
            }
        }
    """
    
    result = await client.query(
        query,
        variables={"id": "doc-123"}
    )
    
    assert result.data["document"]["id"] == "doc-123"
    assert result.data["document"]["status"] == "COMPLETED"
```

---

## 📚 Recursos

- **GraphQL Playground:** http://localhost:8000/api/graphql/
- **Schema SDL:** http://localhost:8000/api/graphql/schema
- **Health Check:** http://localhost:8000/api/graphql/health
- **Documentación oficial:** https://graphql.org/learn/
- **Strawberry docs:** https://strawberry.rocks/

---

## 💡 Tips

1. **Usa fragments** para reutilizar campos comunes
2. **Aprovecha DataLoaders** para optimizar queries
3. **Filtra en el servidor** en vez de en el cliente
4. **Usa paginación** para listas grandes
5. **Maneja errores** con los campos `success` y `message`
6. **Autentica** todas las requests con JWT
7. **Monitorea** las queries lentas con Apollo Studio

---

¡Happy Querying! 🚀

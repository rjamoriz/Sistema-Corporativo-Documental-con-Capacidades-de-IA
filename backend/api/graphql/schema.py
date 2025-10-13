"""
GraphQL Schema
Main schema definition for the FinancIA GraphQL API.
"""

import strawberry
from .resolvers import Query, Mutation


# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)


# Schema SDL (Schema Definition Language) for documentation
SDL = """
type Query {
  \"\"\"Get a single document by ID\"\"\"
  document(id: ID!): Document
  
  \"\"\"Get list of documents with optional filtering\"\"\"
  documents(
    filter: DocumentFilter
    limit: Int = 20
    offset: Int = 0
    orderBy: String = "uploaded_at"
    orderDesc: Boolean = true
  ): [Document!]!
  
  \"\"\"Get paginated documents using cursor-based pagination\"\"\"
  documentsPaginated(
    first: Int = 20
    after: String
    filter: DocumentFilter
  ): DocumentConnection!
  
  \"\"\"Search documents using semantic/vector search\"\"\"
  search(
    query: String!
    limit: Int = 10
    minScore: Float = 0.5
    filter: DocumentFilter
  ): [SearchResult!]!
  
  \"\"\"Query documents using RAG (Retrieval-Augmented Generation)\"\"\"
  ragQuery(
    question: String!
    documentIds: [ID!]
    maxChunks: Int = 5
    temperature: Float = 0.7
  ): RAGResponse!
  
  \"\"\"Get extracted entities, optionally filtered\"\"\"
  entities(
    documentId: ID
    type: EntityType
    limit: Int = 100
  ): [Entity!]!
  
  \"\"\"Get annotations, optionally filtered\"\"\"
  annotations(
    documentId: ID
    userId: ID
  ): [Annotation!]!
  
  \"\"\"Get current authenticated user\"\"\"
  me: User
}

type Mutation {
  \"\"\"Upload a new document\"\"\"
  uploadDocument(
    file: Upload!
    metadata: JSON
  ): UploadResult!
  
  \"\"\"Delete a document\"\"\"
  deleteDocument(id: ID!): DeleteResult!
  
  \"\"\"Add annotation to document\"\"\"
  addAnnotation(input: AnnotationInput!): AnnotationResult!
  
  \"\"\"Update existing annotation\"\"\"
  updateAnnotation(
    id: ID!
    input: AnnotationUpdateInput!
  ): AnnotationResult!
  
  \"\"\"Delete annotation\"\"\"
  deleteAnnotation(id: ID!): DeleteResult!
}

type Document {
  id: ID!
  filename: String!
  mimeType: String!
  size: Int!
  status: DocumentStatus!
  uploadedBy: ID!
  uploadedAt: DateTime!
  processedAt: DateTime
  url: String
  thumbnailUrl: String
  pageCount: Int
  language: String
  confidenceScore: Float
  version: Int!
  metadata: JSON
  
  \"\"\"Entities extracted from document\"\"\"
  entities(type: EntityType): [Entity!]!
  
  \"\"\"Document chunks for RAG\"\"\"
  chunks(limit: Int): [Chunk!]!
  
  \"\"\"Document annotations\"\"\"
  annotations(
    type: AnnotationType
    pageNumber: Int
  ): [Annotation!]!
  
  \"\"\"User who uploaded the document\"\"\"
  uploader: User
  
  \"\"\"Validation results for document\"\"\"
  validationResults: [ValidationResult!]!
}

type Entity {
  id: ID!
  documentId: ID!
  type: EntityType!
  text: String!
  confidence: Float!
  startOffset: Int!
  endOffset: Int!
  pageNumber: Int
  metadata: JSON
}

type Chunk {
  id: ID!
  documentId: ID!
  content: String!
  pageNumber: Int
  chunkIndex: Int!
  embeddingVector: [Float!]
  metadata: JSON
}

type Annotation {
  id: ID!
  documentId: ID!
  userId: ID!
  type: AnnotationType!
  content: String
  pageNumber: Int!
  position: JSON!
  color: String
  createdAt: DateTime!
  updatedAt: DateTime!
  
  \"\"\"Annotation author\"\"\"
  user: User
}

type User {
  id: ID!
  email: String!
  fullName: String
  role: String
  createdAt: DateTime!
}

type SearchResult {
  document: Document!
  score: Float!
  highlights: [String!]!
  matchedChunks: [Chunk!]!
}

type RAGResponse {
  answer: String!
  sources: [Document!]!
  confidence: Float!
  chunksUsed: [Chunk!]!
  metadata: JSON
}

type ValidationResult {
  field: String!
  rule: String!
  passed: Boolean!
  message: String
  severity: String!
}

type DocumentConnection {
  edges: [DocumentEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type DocumentEdge {
  cursor: String!
  node: Document!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type UploadResult {
  document: Document
  success: Boolean!
  message: String
}

type DeleteResult {
  success: Boolean!
  message: String
}

type AnnotationResult {
  annotation: Annotation
  success: Boolean!
  message: String
}

input DocumentFilter {
  status: DocumentStatus
  mimeType: String
  uploadedBy: ID
  uploadedAfter: DateTime
  uploadedBefore: DateTime
  minConfidence: Float
  searchQuery: String
}

input AnnotationInput {
  documentId: ID!
  type: AnnotationType!
  content: String
  pageNumber: Int!
  position: JSON!
  color: String
}

input AnnotationUpdateInput {
  content: String
  position: JSON
  color: String
}

enum DocumentStatus {
  PENDING
  PROCESSING
  COMPLETED
  ERROR
}

enum EntityType {
  PERSON
  ORGANIZATION
  LOCATION
  DATE
  MONEY
  REGULATION
  CONTRACT
  INVOICE
  OTHER
}

enum AnnotationType {
  HIGHLIGHT
  STICKY_NOTE
  REDACTION
  COMMENT
}

scalar DateTime
scalar JSON
scalar Upload
"""


def get_schema_sdl() -> str:
    """
    Get the Schema Definition Language (SDL) as string.
    
    Returns:
        SDL string
    """
    return SDL


from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class EntityType(str, Enum):

    CONCEPT = "CONCEPT"
    AUTHOR = "AUTHOR"
    PAPER = "PAPER"
    METHOD = "METHOD"
    DATASET = "DATASET"
    THEORY = "THEORY"


class RelationType(str, Enum):

    DEFINES = "DEFINES"
    USES = "USES"
    CITES = "CITES"
    AUTHORED = "AUTHORED"
    PROPOSES = "PROPOSES"
    VALIDATES = "VALIDATES"
    CONTRADICTS = "CONTRADICTS"
    EXTENDS = "EXTENDS"
    MENTIONS = "MENTIONS"


class QueryIntent(str, Enum):

    FACTUAL = "FACTUAL"
    COMPARATIVE = "COMPARATIVE"
    CAUSAL = "CAUSAL"
    PROCEDURAL = "PROCEDURAL"
    EXPLORATORY = "EXPLORATORY"


class Entity(BaseModel):

    id: Optional[str] = Field(default=None, description="Unique entity identifier")
    text: str = Field(description="Entity text as it appears in source")
    type: EntityType = Field(description="Entity type classification")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Extraction confidence score"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional entity metadata"
    )


class Relation(BaseModel):

    source_id: str = Field(description="Source entity identifier")
    target_id: str = Field(description="Target entity identifier")
    type: RelationType = Field(description="Relationship type")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Extraction confidence score"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional relation metadata"
    )


class DocumentChunk(BaseModel):

    id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Parent document identifier")
    text: str = Field(description="Chunk text content")
    start_char: int = Field(ge=0, description="Start character position in document")
    end_char: int = Field(ge=0, description="End character position in document")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Chunk metadata (page, section, etc.)"
    )


class GraphNode(BaseModel):

    id: str = Field(description="Node identifier")
    label: str = Field(description="Node label (entity type)")
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Node properties"
    )


class GraphEdge(BaseModel):

    source: str = Field(description="Source node identifier")
    target: str = Field(description="Target node identifier")
    type: str = Field(description="Edge type (relationship)")
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Edge properties"
    )


class GraphPath(BaseModel):

    nodes: list[GraphNode] = Field(description="Nodes in the path")
    edges: list[GraphEdge] = Field(description="Edges connecting the nodes")
    length: int = Field(ge=0, description="Path length (number of edges)")


class ReasoningStep(BaseModel):

    step_number: int = Field(ge=1, description="Step number in sequence")
    description: str = Field(description="What this step accomplishes")
    action: str = Field(description="Action taken (query, inference, etc.)")
    result: str = Field(description="Result of this step")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in this step"
    )


class QueryAnalysis(BaseModel):

    intent: QueryIntent = Field(description="Classified query intent")
    key_entities: list[str] = Field(description="Key entities to search for")
    required_relations: list[str] = Field(description="Required relationship types")
    sub_queries: list[str] = Field(description="Decomposed sub-queries")


class QueryRequest(BaseModel):

    query: str = Field(description="User question")
    session_id: Optional[str] = Field(
        default=None, description="Session identifier for context"
    )
    max_hops: Optional[int] = Field(
        default=None, ge=1, le=10, description="Maximum graph traversal hops"
    )
    include_reasoning: bool = Field(
        default=True, description="Include reasoning trace in response"
    )


class Source(BaseModel):

    document_id: str = Field(description="Source document identifier")
    title: str = Field(description="Document title")
    chunk_id: Optional[str] = Field(default=None, description="Specific chunk cited")
    page: Optional[int] = Field(default=None, description="Page number if applicable")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Source relevance confidence"
    )


class QueryResponse(BaseModel):

    query: str = Field(description="Original user query")
    answer: str = Field(description="Generated answer")
    reasoning_trace: list[ReasoningStep] = Field(
        default_factory=list, description="Chain-of-thought reasoning steps"
    )
    graph_path: Optional[GraphPath] = Field(
        default=None, description="Graph traversal path used"
    )
    sources: list[Source] = Field(
        default_factory=list, description="Source citations"
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Overall answer confidence"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response generation time"
    )


class ReasoningState(BaseModel):

    query: str = Field(description="User query")
    query_analysis: Optional[QueryAnalysis] = Field(
        default=None, description="Query analysis result"
    )
    graph_context: str = Field(default="", description="Retrieved graph context")
    reasoning_steps: list[ReasoningStep] = Field(
        default_factory=list, description="Accumulated reasoning steps"
    )
    current_answer: str = Field(default="", description="Current answer draft")
    graph_path: Optional[GraphPath] = Field(
        default=None, description="Graph traversal path"
    )
    sources: list[Source] = Field(default_factory=list, description="Source citations")
    is_complete: bool = Field(default=False, description="Whether reasoning is done")


class ConversationMessage(BaseModel):

    role: str = Field(description="Message role (user, assistant, system)")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Message timestamp"
    )


class ConversationHistory(BaseModel):

    session_id: str = Field(description="Session identifier")
    messages: list[ConversationMessage] = Field(
        default_factory=list, description="Conversation messages"
    )
    token_count: int = Field(default=0, ge=0, description="Total token count")
    last_updated: datetime = Field(
        default_factory=datetime.now, description="Last update time"
    )

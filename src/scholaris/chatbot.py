
from typing import Any, Optional
from uuid import uuid4

from scholaris.config import Config, load_config
from scholaris.explainability.formatter import ReasoningFormatter
from scholaris.explainability.visualizer import GraphVisualizer
from scholaris.extraction.entities import EntityExtractor
from scholaris.extraction.linker import EntityLinker
from scholaris.extraction.relations import RelationExtractor
from scholaris.graph.builder import GraphBuilder
from scholaris.graph.neo4j_client import Neo4jClient
from scholaris.graph.traversal import GraphTraversal
from scholaris.ingestion.pipeline import IngestionPipeline
from scholaris.llm.client import LLMClient
from scholaris.llm.prompts import PromptManager
from scholaris.memory.context import ContextManager
from scholaris.memory.redis_client import RedisClient
from scholaris.reasoning.cot_engine import ChainOfThoughtEngine
from scholaris.reasoning.query_analyzer import QueryAnalyzer
from scholaris.types import QueryResponse, ReasoningStep, Source
from scholaris.utils.logging import StructuredLogger
from scholaris.vectorstore.chroma_client import ChromaClient
from scholaris.vectorstore.embedder import Embedder

logger = StructuredLogger(__name__)


class ScholarisChatbot:

    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or load_config()

        self._initialize_components()

        logger.info("scholaris_initialized")

    def _initialize_components(self) -> None:
        self.neo4j_client = Neo4jClient(self.config)
        self.redis_client = RedisClient(self.config)
        self.chroma_client = ChromaClient(self.config)

        self.embedder = Embedder(self.config)
        self.llm_client = LLMClient(self.config)
        self.prompt_manager = PromptManager()

        self.entity_extractor = EntityExtractor(self.config)
        self.relation_extractor = RelationExtractor(self.config)
        self.entity_linker = EntityLinker()

        self.graph_builder = GraphBuilder(self.config, self.neo4j_client)
        self.graph_traversal = GraphTraversal(self.config, self.neo4j_client)

        self.context_manager = ContextManager(self.config, self.redis_client)
        self.query_analyzer = QueryAnalyzer(self.config)
        self.cot_engine = ChainOfThoughtEngine(self.config)

        self.formatter = ReasoningFormatter()
        self.visualizer = GraphVisualizer()

        self.ingestion_pipeline = IngestionPipeline()

    def ingest_document(self, file_path: str) -> dict[str, Any]:
        logger.info("ingesting_document", file=file_path)

        document_id, chunks = self.ingestion_pipeline.process_document(file_path)

        all_entities = []
        all_relations = []

        for chunk in chunks:
            entities = self.entity_extractor.extract_entities(chunk.text)
            all_entities.extend(entities)

            relations = self.relation_extractor.extract_relations(
                chunk.text, entities
            )
            all_relations.extend(relations)

        unique_entities = self.entity_extractor.deduplicate_entities(all_entities)

        self.graph_builder.build_graph(unique_entities, all_relations)

        logger.info(
            "document_ingested",
            document_id=document_id,
            chunks=len(chunks),
            entities=len(unique_entities),
            relations=len(all_relations),
        )

        return {
            "document_id": document_id,
            "chunks": len(chunks),
            "entities": len(unique_entities),
            "relations": len(all_relations),
        }

    def ask(
        self,
        query: str,
        session_id: Optional[str] = None,
        max_hops: Optional[int] = None,
        include_reasoning: bool = True,
    ) -> QueryResponse:
        session_id = session_id or str(uuid4())

        logger.info("processing_query", query=query, session_id=session_id)

        analysis = self.query_analyzer.analyze_query(query)

        graph_context = self._retrieve_graph_context(analysis.key_entities, max_hops)

        conversation = self.context_manager.get_conversation(session_id)
        history = self._format_conversation_history(conversation)

        reasoning_steps = []
        if include_reasoning:
            reasoning_steps = self.cot_engine.generate_reasoning_steps(
                query, graph_context
            )

        answer = self._generate_answer(query, graph_context, history)

        self.context_manager.add_message(session_id, "user", query)
        self.context_manager.add_message(session_id, "assistant", answer)

        response = QueryResponse(
            query=query,
            answer=answer,
            reasoning_trace=reasoning_steps,
            sources=[],
            confidence=0.85,
        )

        logger.info("query_processed", session_id=session_id, answer_length=len(answer))

        return response

    def _retrieve_graph_context(
        self, key_entities: list[str], max_hops: Optional[int]
    ) -> str:
        context_parts = []

        for entity_text in key_entities[:3]:
            results = self.graph_traversal.search_entities_by_text(
                entity_text, limit=5
            )

            for result in results:
                node = result.get("n", {})
                if node:
                    context_parts.append(f"Entity: {node.get('text', '')}")

        return "\n".join(context_parts) if context_parts else "No graph context found."

    def _format_conversation_history(self, conversation: Any) -> str:
        if not conversation.messages:
            return "No previous conversation."

        recent_messages = conversation.messages[-5:]
        formatted = []

        for msg in recent_messages:
            formatted.append(f"{msg.role}: {msg.content}")

        return "\n".join(formatted)

    def _generate_answer(
        self, query: str, graph_context: str, history: str
    ) -> str:
        try:
            system_prompt = self.prompt_manager.get_prompt(
                "chain_of_thought", "system"
            )

            user_prompt = self.prompt_manager.format_prompt(
                "chain_of_thought",
                "user_template",
                query=query,
                graph_context=graph_context,
                history=history,
            )

            answer = self.llm_client.generate(user_prompt, system_prompt)
            return answer

        except Exception as e:
            logger.error("answer_generation_failed", error=str(e))
            return "I apologize, but I encountered an error generating an answer."

    def clear_session(self, session_id: str) -> None:
        self.context_manager.clear_conversation(session_id)
        logger.info("session_cleared", session_id=session_id)

    def close(self) -> None:
        self.neo4j_client.close()
        logger.info("scholaris_closed")

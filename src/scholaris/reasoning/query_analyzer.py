
from scholaris.config import Config
from scholaris.types import QueryAnalysis, QueryIntent
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class QueryAnalyzer:

    def __init__(self, config: Config) -> None:
        self.config = config

    def analyze_query(self, query: str) -> QueryAnalysis:
        intent = self._classify_intent(query)
        key_entities = self._extract_key_entities(query)
        required_relations = self._identify_relations(query)
        sub_queries = self._decompose_query(query)

        analysis = QueryAnalysis(
            intent=intent,
            key_entities=key_entities,
            required_relations=required_relations,
            sub_queries=sub_queries,
        )

        logger.info(
            "query_analyzed",
            intent=intent.value,
            entities=len(key_entities),
            sub_queries=len(sub_queries),
        )

        return analysis

    def _classify_intent(self, query: str) -> QueryIntent:
        query_lower = query.lower()

        if any(word in query_lower for word in ["compare", "difference", "versus"]):
            return QueryIntent.COMPARATIVE

        if any(word in query_lower for word in ["why", "because", "cause"]):
            return QueryIntent.CAUSAL

        if any(word in query_lower for word in ["how", "steps", "process"]):
            return QueryIntent.PROCEDURAL

        if any(word in query_lower for word in ["explore", "related", "similar"]):
            return QueryIntent.EXPLORATORY

        return QueryIntent.FACTUAL

    def _extract_key_entities(self, query: str) -> list[str]:
        words = query.split()
        entities = [w for w in words if w.istitle() and len(w) > 3]
        return entities[:5]

    def _identify_relations(self, query: str) -> list[str]:
        relations = []

        query_lower = query.lower()

        if "author" in query_lower or "wrote" in query_lower:
            relations.append("AUTHORED")

        if "cite" in query_lower or "reference" in query_lower:
            relations.append("CITES")

        if "use" in query_lower or "apply" in query_lower:
            relations.append("USES")

        return relations or ["MENTIONS"]

    def _decompose_query(self, query: str) -> list[str]:
        if " and " in query.lower():
            parts = query.split(" and ")
            return [p.strip() for p in parts]

        return [query]

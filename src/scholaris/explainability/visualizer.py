
from typing import Optional

from scholaris.types import GraphPath
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class GraphVisualizer:

    def visualize_path(self, path: Optional[GraphPath]) -> str:
        if not path or not path.nodes:
            return "No graph path available."

        lines = ["## Graph Traversal Path\n"]

        for i, node in enumerate(path.nodes):
            lines.append(f"{i + 1}. **{node.label}**: {node.properties.get('text', node.id)}")

            if i < len(path.edges):
                edge = path.edges[i]
                lines.append(f"   └─ *{edge.type}* →")

        lines.append(f"\nPath length: {path.length} hops")

        visualization = "\n".join(lines)

        logger.debug("path_visualized", nodes=len(path.nodes), edges=len(path.edges))

        return visualization

    def generate_mermaid_diagram(self, path: Optional[GraphPath]) -> str:
        if not path or not path.nodes:
            return "graph LR\n  A[No path available]"

        lines = ["graph LR"]

        for i, node in enumerate(path.nodes):
            node_id = f"N{i}"
            node_label = node.properties.get("text", node.id)[:20]
            lines.append(f'  {node_id}["{node_label}"]')

            if i < len(path.edges):
                edge = path.edges[i]
                next_node_id = f"N{i + 1}"
                lines.append(f"  {node_id} -->|{edge.type}| {next_node_id}")

        diagram = "\n".join(lines)

        logger.debug("mermaid_diagram_generated", nodes=len(path.nodes))

        return diagram

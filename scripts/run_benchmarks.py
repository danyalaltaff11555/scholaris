"""
Benchmarking and evaluation script.

Runs performance benchmarks and accuracy tests.
"""

import time

from scholaris.chatbot import ScholarisChatbot
from scholaris.config import load_config
from scholaris.utils.logging import setup_logging

logger = setup_logging("INFO")


def benchmark_query_latency(chatbot: ScholarisChatbot, queries: list[str]) -> None:
    """Benchmark query processing latency."""
    logger.info("Running query latency benchmark...")

    latencies = []

    for query in queries:
        start_time = time.time()
        chatbot.ask(query)
        latency = time.time() - start_time
        latencies.append(latency)

        logger.info(f"Query: {query[:50]}... | Latency: {latency:.2f}s")

    avg_latency = sum(latencies) / len(latencies)
    logger.info(f"Average latency: {avg_latency:.2f}s")


def run_benchmarks():
    """Run all benchmarks."""
    config = load_config()
    chatbot = ScholarisChatbot(config)

    test_queries = [
        "What is machine learning?",
        "How do neural networks work?",
        "What are transformers in NLP?",
    ]

    benchmark_query_latency(chatbot, test_queries)

    chatbot.close()
    logger.info("Benchmarks complete!")


if __name__ == "__main__":
    run_benchmarks()

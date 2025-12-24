import tiktoken

from scholaris.config import Config
from scholaris.memory.redis_client import RedisClient
from scholaris.types import ConversationHistory, ConversationMessage
from scholaris.utils.logging import StructuredLogger

logger = StructuredLogger(__name__)


class ContextManager:

    def __init__(self, config: Config, redis_client: RedisClient) -> None:
        self.config = config
        self.redis = redis_client
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def get_conversation(self, session_id: str) -> ConversationHistory:
        key = f"conversation:{session_id}"
        data = self.redis.get(key)

        if data:
            return ConversationHistory(**data)

        return ConversationHistory(session_id=session_id)

    def add_message(
        self, session_id: str, role: str, content: str
    ) -> ConversationHistory:
        conversation = self.get_conversation(session_id)

        message = ConversationMessage(role=role, content=content)
        conversation.messages.append(message)

        conversation.token_count = self._count_tokens(conversation)

        self._save_conversation(conversation)

        logger.info(
            "message_added",
            session_id=session_id,
            role=role,
            tokens=conversation.token_count,
        )

        return conversation

    def should_summarize(self, conversation: ConversationHistory) -> bool:
        return conversation.token_count >= self.config.context.summarization_trigger

    def _count_tokens(self, conversation: ConversationHistory) -> int:
        total = 0
        for message in conversation.messages:
            tokens = len(self.encoder.encode(message.content))
            total += tokens
        return total

    def _save_conversation(self, conversation: ConversationHistory) -> None:
        key = f"conversation:{conversation.session_id}"
        self.redis.set(key, conversation.model_dump(), ttl=self.config.redis.ttl)

    def clear_conversation(self, session_id: str) -> None:
        key = f"conversation:{session_id}"
        self.redis.delete(key)
        logger.info("conversation_cleared", session_id=session_id)

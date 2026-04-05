from services.embedding_service import M3EEmbeddingService
from services.vector_store import QdrantVectorStore
from services.llm_service import ZhipuService
from services.cache_service import CacheService
from services.memory_service import MemoryService
from utils.logger import setup_logger

logger = setup_logger("rag")

class RAGService:
    def __init__(self):
        self.embedding_service = M3EEmbeddingService()
        self.vector_store = QdrantVectorStore()
        self.llm_service = ZhipuService()
        self.cache_service = CacheService(ttl_hours=24)
        self.memory_service = MemoryService(max_history=10)  # 记忆服务
        logger.info("RAG服务初始化完成（含记忆功能）")

    def query(self, user_query, user_id="default"):
        """
        RAG查询（支持对话记忆）

        Args:
            user_query: 用户问题
            user_id: 用户ID（用于记忆管理）

        Returns:
            查询结果字典
        """
        # 先检查缓存
        cached_answer = self.cache_service.get(user_query)
        if cached_answer:
            logger.info(f"缓存命中: {user_query[:50]}...")
            # 仍然保存到记忆中
            self.memory_service.add_message(user_id, "user", user_query)
            self.memory_service.add_message(user_id, "assistant", cached_answer)
            return {"answer": cached_answer, "source": "cache"}

        # 缓存未命中，执行RAG查询
        logger.info(f"执行RAG查询: {user_query[:50]}...")

        try:
            # 获取对话历史（用于上下文）
            conversation_context = self.memory_service.get_context_string(user_id, limit=3)

            # 向量检索
            query_embedding = self.embedding_service.encode_single(user_query)
            results = self.vector_store.search(query_embedding, limit=3)

            context_parts = []
            for result in results:
                content = result.get("text", "")
                context_parts.append(content)

            # 组装上下文：对话历史 + 知识库
            context_parts_all = []
            if conversation_context:
                context_parts_all.append(f"对话历史：\n{conversation_context}")
            
            # 知识库内容拼接（先拼接再添加）
            knowledge_content = "\n\n".join(context_parts)
            context_parts_all.append(f"知识库内容：\n{knowledge_content}")

            full_context = "\n\n".join(context_parts_all)

            system_prompt = "你是一个爱室丽家居的专业智能助手，请基于提供的知识库内容和对话历史准确回答用户关于家居产品的询问。如果知识库中没有相关信息，请诚实地告知用户。"

            response = self.llm_service.chat_with_context(
                user_query=user_query,
                context=full_context,
                system_prompt=system_prompt
            )

            # 保存到缓存
            self.cache_service.set(user_query, response)

            # 保存到记忆
            self.memory_service.add_message(user_id, "user", user_query)
            self.memory_service.add_message(user_id, "assistant", response)

            logger.info(f"RAG查询成功，已缓存并保存到记忆")
            return {"answer": response, "source": "rag"}

        except Exception as e:
            logger.error(f"RAG查询失败: {str(e)}")
            raise

from utils.logger import setup_logger

logger = setup_logger("error_handler")

class ErrorHandler:
    """统一错误处理"""
    
    @staticmethod
    def handle_llm_error(e):
        """处理LLM相关错误"""
        error_msg = str(e)
        if "API key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "AI服务认证失败，请检查API配置"
        elif "rate limit" in error_msg.lower():
            return "请求过于频繁，请稍后再试"
        elif "timeout" in error_msg.lower():
            return "AI服务响应超时，请重试"
        else:
            logger.error(f"LLM错误: {error_msg}")
            return "AI服务暂时不可用，请稍后再试"
    
    @staticmethod
    def handle_vector_error(e):
        """处理向量数据库错误"""
        error_msg = str(e)
        if "connection" in error_msg.lower():
            return "向量数据库连接失败，请检查服务状态"
        elif "collection" in error_msg.lower():
            return "知识库数据异常，请联系管理员"
        else:
            logger.error(f"向量数据库错误: {error_msg}")
            return "检索服务暂时不可用"
    
    @staticmethod
    def handle_embedding_error(e):
        """处理Embedding错误"""
        logger.error(f"Embedding错误: {str(e)}")
        return "文本向量化失败，请稍后再试"

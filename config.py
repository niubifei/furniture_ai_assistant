# 配置文件
import os
from dotenv import load_dotenv

load_dotenv()

# ========== 智谱 GLM-4-Flash 配置 ==========
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_MODEL = "glm-4-flash"
LLM_MODEL = "glm-4-flash"

# ========== M3E-Base 嵌入模型配置 ==========
M3E_MODEL_NAME = "moka-ai/m3e-base"
M3E_DEVICE = "cpu"
EMBEDDING_MODEL = "moka-ai/m3e-base"
EMBEDDING_DIM = 768

# ========== Qdrant 向量数据库配置 ==========
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "furniture_knowledge"

# ========== API 服务配置 ==========
API_HOST = "0.0.0.0"
API_PORT = 8000

# ========== 日志配置 ==========
LOG_LEVEL = "INFO"
LOG_FILE = "logs/ai_assistant.log"

# ========== Redis 缓存配置 ==========
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

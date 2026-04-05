from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.rag_service import RAGService
from services.agent_service import AgentService
from services.analytics_service import AnalyticsService
import time
import uvicorn

app = FastAPI(title="爱室丽家居AI智能助手", version="2.0.0")

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
rag_service = RAGService()
agent_service = AgentService()
analytics_service = AnalyticsService()

class ChatRequest(BaseModel):
    query: str
    mode: str = "rag"
    user_id: str = "default"  # 用户ID，用于对话记忆

class ChatResponse(BaseModel):
    answer: str
    mode: str
    source: str = None

@app.get("/")
async def root():
    return {
        "service": "爱室丽家居AI智能助手",
        "version": "2.0.0",
        "features": ["RAG检索", "Agent工具调用", "缓存优化", "日志监控"],
        "models": {
            "llm": "GLM-4-Flash",
            "embedding": "M3E-Base",
            "vector_db": "Qdrant"
        },
        "modes": {
            "rag": "基于知识库的检索增强生成",
            "agent": "智能体模式，支持工具调用（库存查询、产品信息、促销活动）"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI助手", "version": "2.0.0"}

@app.get("/stats")
def get_stats():
    """获取统计信息"""
    return analytics_service.get_stats()

@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.time()
    answer = None
    source = None
    error = None

    try:
        if request.mode == "rag":
            # RAG模式：基于知识库检索
            result = rag_service.query(request.query, user_id=request.user_id)
            answer = result["answer"]
            source = result["source"]
        
        elif request.mode == "agent":
            # Agent模式：支持工具调用
            answer = agent_service.run(request.query, user_id=request.user_id)
            source = "agent"
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的对话模式: {request.mode}，可选模式: rag, agent")

        response_time = int((time.time() - start_time) * 1000)

        # 记录分析日志
        analytics_service.log_request(
            query=request.query,
            answer=answer,
            source=source,
            response_time_ms=response_time
        )

        return ChatResponse(answer=answer, mode=request.mode, source=source)

    except Exception as e:
        error = str(e)
        response_time = int((time.time() - start_time) * 1000)

        # 记录错误日志
        analytics_service.log_request(
            query=request.query,
            answer="",
            source="error",
            response_time_ms=response_time,
            error=error
        )

        raise HTTPException(status_code=500, detail=f"服务错误: {error}")

if __name__ == "__main__":
    # 启动服务（Windows兼容版本）
    # 注意：workers和uvloop参数在Windows上不支持
    # 如需生产级高并发，请使用Gunicorn或部署到Linux服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
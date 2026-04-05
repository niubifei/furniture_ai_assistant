# 爱室丽家居 AI 智能助手

基于 RAG 技术的家居产品咨询系统 v2.0

## 项目简介

本项目是一个智能客服系统，结合了 RAG（检索增强生成）和 Agent 智能体两种模式，为用户提供家居产品咨询服务。

### 核心特性

- **双模式切换**：RAG 检索模式 + Agent 智能模式
- **向量检索**：基于 M3E-Base 模型的语义相似度搜索
- **对话记忆**：支持多轮对话，记住用户偏好
- **工具调用**：Agent 可调用预定义工具查询库存、价格、促销信息
- **本地部署**：所有服务可本地运行，数据安全可控

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端界面                            │
│                   (index.html)                          │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP API
┌─────────────────────▼───────────────────────────────────┐
│                   FastAPI 后端                           │
│                    (main.py)                            │
├─────────────────┬─────────────────┬─────────────────────┤
│   RAG Service   │  Agent Service  │   Memory Service    │
│  (rag_service)  │ (agent_service) │ (memory_service)    │
├─────────────────┴─────────────────┴─────────────────────┤
│              Embedding Service (M3E-Base)               │
├─────────────────────────────────────────────────────────┤
│              Vector Store (Qdrant)                      │
├─────────────────────────────────────────────────────────┤
│              LLM (智谱 GLM-4-Flash)                     │
└─────────────────────────────────────────────────────────┘
```

## 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | FastAPI | 高性能异步 API 框架 |
| 向量数据库 | Qdrant | 高效的向量相似度搜索 |
| 嵌入模型 | M3E-Base | 中文语义向量模型 (768维) |
| 大语言模型 | 智谱 GLM-4-Flash | 国产大模型，支持 Function Calling |
| 前端 | HTML/CSS/JavaScript | 纯前端，无需框架 |

## 快速开始

### 1. 环境要求

- Python 3.8+
- Qdrant 向量数据库

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动 Qdrant

```bash
# 使用 Docker 启动 Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

### 4. 配置 API Key

编辑 `config.py`，填入你的智谱 API Key：

```python
ZHIPU_API_KEY = "你的API Key"
```

获取地址：https://open.bigmodel.cn

### 5. 导入知识库

```bash
python scripts/import_knowledge.py
```

### 6. 启动服务

```bash
python main.py
```

服务启动后访问：http://localhost:8000

### 7. 打开前端

直接用浏览器打开 `index.html` 文件

## 项目结构

```
furniture_ai_assistant/
├── main.py                 # FastAPI 主入口
├── config.py               # 配置文件
├── index.html              # 前端界面
├── requirements.txt        # 依赖列表
├── data/
│   └── furniture_knowledge.json  # 知识库数据
├── services/
│   ├── rag_service.py      # RAG 检索服务
│   ├── agent_service.py    # Agent 智能体服务
│   ├── embedding_service.py # 向量嵌入服务
│   ├── vector_store.py     # Qdrant 向量数据库
│   ├── memory_service.py   # 对话记忆服务
│   └── cache_service.py    # 缓存服务
├── scripts/
│   └── import_knowledge.py # 知识库导入脚本
└── utils/
    ├── logger.py           # 日志工具
    └── error_handler.py    # 错误处理
```

## API 接口

### 对话接口

```http
POST /chat
Content-Type: application/json

{
  "query": "你们家有什么沙发？",
  "mode": "rag",
  "session_id": "user001"
}
```

**响应：**

```json
{
  "answer": "我们爱室丽家居有ASH-001沙发...",
  "source": "rag"
}
```

### 健康检查

```http
GET /health
```

## 功能对比

| 功能 | RAG 模式 | Agent 模式 |
|------|:--------:|:----------:|
| 知识库检索 | ✅ | ✅ |
| 多轮对话记忆 | ❌ | ✅ |
| 工具调用 | ❌ | ✅ |
| 响应速度 | 快 | 较慢 |
| 适用场景 | 单次查询 | 复杂对话 |

## 面试亮点

1. **RAG 架构设计**：向量检索 + LLM 生成，解决大模型知识更新问题
2. **双模式切换**：灵活适配不同业务场景
3. **Agent Function Calling**：工具调用实现业务闭环
4. **对话记忆机制**：基于会话的多轮对话支持
5. **本地向量数据库**：数据安全，部署灵活

## 扩展方向

- 接入真实产品数据库
- 添加用户认证系统
- 支持图片检索（多模态 RAG）
- 添加对话评价反馈机制
- 部署到云服务器

## License

MIT License

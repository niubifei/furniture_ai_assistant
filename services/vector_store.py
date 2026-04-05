from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, HnswConfigDiff
from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME
import uuid

class QdrantVectorStore:
    """Qdrant 向量数据库服务"""
    
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.collection_name = QDRANT_COLLECTION_NAME
        self.embedding_dim = 768
        self._ensure_collection()
    
    def _ensure_collection(self):
        """确保集合存在，不存在则创建"""
        # 检查集合是否存在
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        collection_exists = self.collection_name in collection_names
        
        if not collection_exists:
            print(f"正在创建集合: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(
                        m=32,
                        ef_construct=200
                    )
                )
            )
            print(f"集合创建成功: {self.collection_name} (HNSW优化: M=32, ef_construct=200)")
    
    def insert_documents(self, documents):
        """插入文档到向量数据库"""
        points = []
        for doc in documents:
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=doc["vector"],
                payload={
                    "text": doc["text"],
                    **doc.get("metadata", {})
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"成功插入 {len(points)} 条文档")
    
    def search(self, query_vector, limit=5, score_threshold=0.5):
        """向量相似度搜索"""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            formatted_results = []
            for result in results:
                # 兼容不同版本的payload字段名
                text = result.payload.get("content") or result.payload.get("text", "")
                
                formatted_results.append({
                    "text": text,
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k not in ["text", "content"]}
                })
            
            return formatted_results
        
        except Exception as e:
            print(f"搜索失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

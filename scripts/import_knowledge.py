import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.embedding_service import M3EEmbeddingService as M3EService
from services.vector_store import QdrantVectorStore
import json

def import_documents(file_path="data/furniture_knowledge.json"):
    print("正在加载知识库...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    embedding_model = M3EService()
    vector_store = QdrantVectorStore()
    
    print("正在生成向量...")
    texts = [doc["text"] for doc in documents]
    vectors = embedding_model.encode(texts, show_progress=True)
    
    documents_with_vectors = []
    for doc, vector in zip(documents, vectors):
        documents_with_vectors.append({
            "text": doc["text"],
            "vector": vector,
            "metadata": doc.get("metadata", {})
        })
    
    print("正在插入向量数据库...")
    vector_store.insert_documents(documents_with_vectors)
    
    print(f"知识库导入完成！共导入 {len(documents)} 条文档")

if __name__ == "__main__":
    import_documents()
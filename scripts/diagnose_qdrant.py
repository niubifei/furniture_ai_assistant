"""
诊断脚本 - 检查Qdrant数据库状态和数据
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME

def diagnose():
    print("=" * 60)
    print("Qdrant 数据库诊断")
    print("=" * 60)
    
    # 连接Qdrant
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 1. 检查集合是否存在
    print("\n1. 检查集合是否存在...")
    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        print(f"   当前所有集合: {collection_names}")
        
        if QDRANT_COLLECTION_NAME in collection_names:
            print(f"   ✅ 集合 '{QDRANT_COLLECTION_NAME}' 存在")
        else:
            print(f"   ❌ 集合 '{QDRANT_COLLECTION_NAME}' 不存在")
            print(f"   提示: 请先运行 'python scripts/import_knowledge.py' 导入知识库")
            return
    except Exception as e:
        print(f"   ❌ 获取集合列表失败: {str(e)}")
        return
    
    # 2. 检查数据内容
    print("\n2. 检查数据内容...")
    try:
        # 使用scroll方法获取数据
        result = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=3,
            with_payload=True,
            with_vectors=False
        )
        
        points = result[0]  # scroll返回(points, next_page_offset)
        
        if points:
            print(f"   ✅ 找到 {len(points)} 条数据")
            for i, point in enumerate(points, 1):
                print(f"\n   --- 数据 {i} ---")
                print(f"   ID: {point.id}")
                print(f"   Payload字段: {list(point.payload.keys())}")
                
                # 显示payload内容
                if 'text' in point.payload:
                    print(f"   文本内容: {point.payload['text'][:100]}...")
                elif 'content' in point.payload:
                    print(f"   内容: {point.payload['content'][:100]}...")
                else:
                    # 显示所有payload内容
                    print(f"   Payload: {str(point.payload)[:200]}")
        else:
            print(f"   ❌ 集合中没有数据")
            print(f"   提示: 请先运行 'python scripts/import_knowledge.py' 导入知识库")
            return
    except Exception as e:
        print(f"   ❌ 获取数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 测试搜索功能
    print("\n3. 测试搜索功能...")
    try:
        import numpy as np
        # 创建一个随机向量用于测试
        test_vector = np.random.rand(768).tolist()
        
        results = client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=test_vector,
            limit=2
        )
        
        if results:
            print(f"   ✅ 搜索成功，返回 {len(results)} 条结果")
            for i, result in enumerate(results, 1):
                print(f"\n   --- 结果 {i} ---")
                print(f"   分数: {result.score}")
                print(f"   Payload字段: {list(result.payload.keys())}")
                
                if 'text' in result.payload:
                    print(f"   文本: {result.payload['text'][:80]}...")
                elif 'content' in result.payload:
                    print(f"   内容: {result.payload['content'][:80]}...")
                else:
                    print(f"   Payload: {str(result.payload)[:200]}")
        else:
            print(f"   ❌ 搜索没有返回结果")
    except Exception as e:
        print(f"   ❌ 搜索失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    diagnose()

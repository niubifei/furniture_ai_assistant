import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("开始测试API接口")
    print("=" * 50)
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False
    
    # 测试问答接口
    print("\n2. 测试问答接口...")
    test_queries = [
        "你们家有没有实木沙发？",
        "客厅茶几什么材质的？",
        "沙发能定制尺寸吗？"
        "床垫有哪些类型？", 
        "保修政策是怎样的？"
    ]
    
    for query in test_queries:
        print(f"\n问题: {query}")
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"query": query},
                timeout=30
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"回答: {result['response'][:100]}...")
            else:
                print(f"❌ 请求失败: {response.text}")
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_api()
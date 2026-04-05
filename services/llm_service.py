from zhipuai import ZhipuAI
from config import LLM_MODEL, ZHIPU_API_KEY

class ZhipuService:
    def __init__(self):
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model = LLM_MODEL
    
    def chat(self, messages, temperature=0.7, max_tokens=1024):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def chat_with_context(self, user_query, context, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({
            "role": "user",
            "content": f"基于以下知识库内容回答用户问题：\n\n知识库：\n{context}\n\n用户问题：{user_query}"
        })
        
        return self.chat(messages)
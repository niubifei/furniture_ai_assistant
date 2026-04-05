from zhipuai import ZhipuAI
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ZHIPU_API_KEY, LLM_MODEL
from services.memory_service import MemoryService
from utils.logger import setup_logger
import json

# 兼容不同的配置变量名
ZHIPU_MODEL = LLM_MODEL

logger = setup_logger("agent")

class AgentService:
    """
    增强版智能体服务 - 支持工具调用和对话记忆

    特性：
    1. Function Calling：自动调用预定义工具
    2. 对话记忆：支持多轮对话，记住用户偏好
    3. 任务拆解：基于用户问题自动选择合适的工具
    """

    def __init__(self):
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model = ZHIPU_MODEL
        self.tools = self._define_tools()
        self.memory_service = MemoryService(max_history=10)
        logger.info("Agent服务初始化完成（含记忆功能）")

    def _define_tools(self):
        """定义Agent可用的工具"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_inventory",
                    "description": "查询产品库存状态，返回库存数量、仓库位置和状态",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sku": {
                                "type": "string",
                                "description": "产品SKU编码，如：SFA-001"
                            }
                        },
                        "required": ["sku"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "获取产品详细信息，包括价格、材质、尺寸等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {
                                "type": "string",
                                "description": "产品名称，如：北欧实木沙发"
                            }
                        },
                        "required": ["product_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_promotion_info",
                    "description": "查询促销活动信息，包括折扣、活动时间等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "产品类别，如：沙发、床垫、茶几"
                            }
                        },
                        "required": ["category"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name, tool_args):
        """执行工具调用（模拟实现）"""
        logger.info(f"执行工具: {tool_name}, 参数: {tool_args}")

        if tool_name == "check_inventory":
            # 模拟库存查询（实际应连接数据库）
            sku = tool_args.get("sku", "")
            return {
                "sku": sku,
                "stock": 150,
                "warehouse": "北京仓",
                "status": "有货",
                "delivery_time": "2-3天"
            }

        elif tool_name == "get_product_info":
            # 模拟产品信息查询（实际应连接数据库）
            product_name = tool_args.get("product_name", "")
            return {
                "name": product_name,
                "price": 2999,
                "original_price": 3999,
                "category": "沙发",
                "material": "实木框架+高弹海绵",
                "size": "220*95*85cm",
                "color": "米白色/深灰色",
                "warranty": "3年质保"
            }

        elif tool_name == "get_promotion_info":
            # 模拟促销信息查询
            category = tool_args.get("category", "")
            return {
                "category": category,
                "discount": "满3000减500",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "special_offer": "免费配送+安装"
            }

        else:
            logger.error(f"未知工具: {tool_name}")
            return {"error": f"未知工具: {tool_name}"}

    def run(self, user_query, user_id="default"):
        """
        运行智能体（支持对话记忆）

        Args:
            user_query: 用户问题
            user_id: 用户ID

        Returns:
            智能体回答
        """
        logger.info(f"Agent运行 - 用户: {user_id}, 问题: {user_query[:50]}...")

        # 获取对话历史
        conversation_history = self.memory_service.get_conversation_history(user_id, limit=6)

        # 构建消息列表（包含历史对话）
        messages = []

        # 添加历史对话
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 添加当前问题
        messages.append({"role": "user", "content": user_query})

        # 添加系统提示
        system_message = {
            "role": "system",
            "content": """你是爱室丽家居的智能客服助手，能够调用工具帮助用户查询产品信息、库存和促销活动。
            使用规则：
            1. 当用户询问库存时，调用check_inventory工具
            2. 当用户询问产品详情时，调用get_product_info工具
            3. 当用户询问促销活动时，调用get_promotion_info工具
            4. 结合工具返回的信息，给出友好的回答
            5. 如果工具调用失败，诚实地告知用户并提供其他帮助"""
        }

        messages.insert(0, system_message)

        try:
            # 第一次调用：决定是否使用工具
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # 如果需要调用工具
            if message.tool_calls:
                logger.info(f"检测到工具调用: {len(message.tool_calls)} 个")

                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    result = self._execute_tool(tool_name, tool_args)
                    tool_results.append({
                        "tool_name": tool_name,
                        "result": result
                    })

                # 第二次调用：基于工具结果生成回答
                # 将message转换为字典格式，避免JSON序列化错误
                messages.append({
                    "role": message.role,
                    "content": message.content,
                    "tool_calls": [{
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls]
                })

                # 添加工具返回结果
                for tool_call, tool_result in zip(message.tool_calls, tool_results):
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result["result"], ensure_ascii=False)
                    })

                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )

                answer = final_response.choices[0].message.content
                logger.info(f"Agent回答（工具调用）: {answer[:50]}...")

                # 保存到记忆
                self.memory_service.add_message(user_id, "user", user_query)
                self.memory_service.add_message(user_id, "assistant", answer)

                return answer

            else:
                # 不需要调用工具，直接回答
                answer = message.content
                logger.info(f"Agent回答（直接）: {answer[:50]}...")

                # 保存到记忆
                self.memory_service.add_message(user_id, "user", user_query)
                self.memory_service.add_message(user_id, "assistant", answer)

                return answer

        except Exception as e:
            logger.error(f"Agent运行失败: {str(e)}")
            raise Exception(f"智能体运行失败: {str(e)}")

    def clear_memory(self, user_id="default"):
        """清空指定用户的对话记忆"""
        self.memory_service.clear_conversation(user_id)
        logger.info(f"用户 {user_id} 的对话记忆已清空")

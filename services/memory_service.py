"""
对话记忆服务 - 基于Mem0实现
支持多轮对话上下文管理
"""

from typing import List, Optional
import json
from utils.logger import setup_logger

logger = setup_logger("memory")

class MemoryService:
    """
    对话记忆服务（简化版实现）

    注意：完整版Mem0需要安装：pip install mem0ai
    这里使用文件存储实现，用于演示记忆管理功能
    """

    def __init__(self, max_history: int = 10):
        """
        初始化记忆服务

        Args:
            max_history: 最大保存的历史对话数量
        """
        self.max_history = max_history
        # 使用字典存储多用户的对话历史
        # 格式: {user_id: [{"role": "user/assistant", "content": "..."}, ...]}
        self.conversations = {}
        logger.info(f"记忆服务初始化完成（最大历史: {max_history}条）")

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """
        添加一条对话消息

        Args:
            user_id: 用户ID
            role: 角色（user或assistant）
            content: 消息内容
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        # 添加新消息
        self.conversations[user_id].append({
            "role": role,
            "content": content
        })

        # 限制历史数量
        if len(self.conversations[user_id]) > self.max_history * 2:  # 乘以2因为包含user和assistant
            self.conversations[user_id] = self.conversations[user_id][-self.max_history * 2:]

        logger.debug(f"用户 {user_id} 添加消息: {role} - {content[:50]}...")

    def get_conversation_history(self, user_id: str, limit: Optional[int] = None) -> List[dict]:
        """
        获取用户的对话历史

        Args:
            user_id: 用户ID
            limit: 返回的历史数量（None表示返回全部）

        Returns:
            对话历史列表
        """
        if user_id not in self.conversations:
            return []

        history = self.conversations[user_id]

        if limit:
            return history[-limit:]

        return history

    def get_context_string(self, user_id: str, limit: int = 5) -> str:
        """
        获取格式化的对话上下文字符串

        Args:
            user_id: 用户ID
            limit: 返回的历史轮数（一轮=用户+助手）

        Returns:
            格式化的对话历史字符串
        """
        history = self.get_conversation_history(user_id, limit * 2)  # 乘以2因为包含user和assistant

        if not history:
            return ""

        context_parts = []
        for msg in history:
            role_name = "用户" if msg["role"] == "user" else "助手"
            context_parts.append(f"{role_name}: {msg['content']}")

        return "\n".join(context_parts)

    def clear_conversation(self, user_id: str) -> None:
        """
        清空指定用户的对话历史

        Args:
            user_id: 用户ID
        """
        if user_id in self.conversations:
            self.conversations[user_id] = []
            logger.info(f"用户 {user_id} 对话历史已清空")

    def save_to_file(self, filepath: str = "data/conversations.json") -> None:
        """
        保存对话历史到文件

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
            logger.info(f"对话历史已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存对话历史失败: {str(e)}")

    def load_from_file(self, filepath: str = "data/conversations.json") -> None:
        """
        从文件加载对话历史

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.conversations = json.load(f)
            logger.info(f"对话历史已从 {filepath} 加载")
        except FileNotFoundError:
            logger.warning(f"文件不存在: {filepath}")
        except Exception as e:
            logger.error(f"加载对话历史失败: {str(e)}")

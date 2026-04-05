import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from utils.logger import setup_logger

logger = setup_logger("cache")

class CacheService:
    """简单的文件缓存服务"""
    
    def __init__(self, cache_dir="cache", ttl_hours=24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, query):
        """生成缓存键"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, query):
        """获取缓存的回答"""
        cache_key = self._get_cache_key(query)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_path.unlink()
                logger.info(f"缓存过期: {query}")
                return None
            
            logger.info(f"缓存命中: {query}")
            return cache_data['answer']
        
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            return None
    
    def set(self, query, answer):
        """保存回答到缓存"""
        cache_key = self._get_cache_key(query)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'query': query,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"缓存保存: {query}")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def clear(self):
        """清空所有缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info("缓存已清空")

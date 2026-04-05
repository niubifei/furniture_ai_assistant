import json
from pathlib import Path
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger("analytics")

class AnalyticsService:
    """请求日志和分析服务"""
    
    def __init__(self, log_dir="logs/analytics"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_request(self, query, answer, source, response_time_ms=None, error=None):
        """记录请求日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "answer": answer,
            "source": source,
            "response_time_ms": response_time_ms,
            "error": error
        }
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"requests_{date_str}.jsonl"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
            logger.info(f"请求日志已保存: {query[:50]}...")
        except Exception as e:
            logger.error(f"保存日志失败: {e}")
    
    def get_stats(self, date_str=None):
        """获取统计信息"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        log_file = self.log_dir / f"requests_{date_str}.jsonl"
        
        if not log_file.exists():
            return {"total": 0, "cache_hits": 0, "rag_queries": 0, "errors": 0}
        
        stats = {"total": 0, "cache_hits": 0, "rag_queries": 0, "errors": 0}
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_data = json.loads(line)
                    stats["total"] += 1
                    if log_data.get("source") == "cache":
                        stats["cache_hits"] += 1
                    elif log_data.get("source") == "rag":
                        stats["rag_queries"] += 1
                    if log_data.get("error"):
                        stats["errors"] += 1
        except Exception as e:
            logger.error(f"读取统计信息失败: {e}")
        
        return stats

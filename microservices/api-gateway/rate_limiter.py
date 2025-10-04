"""
限流器实现
基于Redis的分布式限流
"""
import time
import asyncio
from typing import Optional
import redis
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """限流器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限流键（如用户ID、IP等）
            limit: 限制次数
            window: 时间窗口（秒）
        
        Returns:
            bool: 是否允许请求
        """
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # 使用Redis Pipeline提高性能
            pipe = self.redis.pipeline()
            
            # 移除过期的记录
            pipe.zremrangebyscore(key, 0, window_start)
            
            # 获取当前窗口内的请求数
            pipe.zcard(key)
            
            # 添加当前请求
            pipe.zadd(key, {str(current_time): current_time})
            
            # 设置过期时间
            pipe.expire(key, window)
            
            # 执行Pipeline
            results = pipe.execute()
            current_count = results[1]
            
            # 检查是否超过限制
            if current_count >= limit:
                logger.warning(f"Rate limit exceeded for key: {key}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # 发生错误时允许请求通过
            return True
    
    async def get_remaining_requests(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> int:
        """获取剩余请求次数"""
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # 清理过期记录
            self.redis.zremrangebyscore(key, 0, window_start)
            
            # 获取当前计数
            current_count = self.redis.zcard(key)
            
            return max(0, limit - current_count)
            
        except Exception as e:
            logger.error(f"Get remaining requests error: {e}")
            return limit
    
    async def reset_limit(self, key: str):
        """重置限流计数"""
        try:
            self.redis.delete(key)
            logger.info(f"Rate limit reset for key: {key}")
        except Exception as e:
            logger.error(f"Reset rate limit error: {e}")

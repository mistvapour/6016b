"""
熔断器实现
用于防止级联故障，提高系统稳定性
"""
import time
import asyncio
from enum import Enum
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态

class CircuitBreaker:
    """熔断器"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        return (
            self.state == CircuitState.OPEN and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _record_success(self):
        """记录成功调用"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker reset to CLOSED state")
    
    def _record_failure(self):
        """记录失败调用"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数调用"""
        
        # 检查熔断器状态
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 记录成功
            if self.state == CircuitState.HALF_OPEN:
                self._record_success()
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0  # 重置失败计数
            
            return result
            
        except self.expected_exception as e:
            # 记录失败
            self._record_failure()
            logger.error(f"Circuit breaker recorded failure: {e}")
            raise
        except Exception as e:
            # 其他异常不记录为失败
            logger.error(f"Unexpected error in circuit breaker: {e}")
            raise

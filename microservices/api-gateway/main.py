#!/usr/bin/env python3
"""
API网关服务
统一入口，路由分发，认证授权，限流熔断
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
import redis
import json
from circuit_breaker import CircuitBreaker
from rate_limiter import RateLimiter

# 配置
GATEWAY_CONFIG = {
    "title": "MIL-STD-6016 API Gateway",
    "version": "1.0.0",
    "description": "微服务API网关",
    "services": {
        "pdf-service": "http://pdf-service:8001",
        "semantic-service": "http://semantic-service:8002", 
        "cdm-service": "http://cdm-service:8003",
        "import-service": "http://import-service:8004",
        "user-service": "http://user-service:8005",
        "config-service": "http://config-service:8006",
        "monitor-service": "http://monitor-service:8007",
        "storage-service": "http://storage-service:8008"
    },
    "rate_limits": {
        "default": {"requests": 100, "window": 60},
        "pdf-service": {"requests": 10, "window": 60},
        "semantic-service": {"requests": 50, "window": 60}
    },
    "circuit_breaker": {
        "failure_threshold": 5,
        "recovery_timeout": 30,
        "expected_exception": httpx.HTTPError
    }
}

# 创建FastAPI应用
app = FastAPI(
    title=GATEWAY_CONFIG["title"],
    version=GATEWAY_CONFIG["version"],
    description=GATEWAY_CONFIG["description"]
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis连接（用于限流和缓存）
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# 限流器
rate_limiter = RateLimiter(redis_client)

# 熔断器
circuit_breakers = {
    service: CircuitBreaker(
        failure_threshold=GATEWAY_CONFIG["circuit_breaker"]["failure_threshold"],
        recovery_timeout=GATEWAY_CONFIG["circuit_breaker"]["recovery_timeout"],
        expected_exception=GATEWAY_CONFIG["circuit_breaker"]["expected_exception"]
    )
    for service in GATEWAY_CONFIG["services"]
}

# HTTP客户端
http_client = httpx.AsyncClient(timeout=30.0)

# 请求模型
class ProxyRequest(BaseModel):
    method: str
    path: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None

# 认证中间件
async def authenticate_request(request: Request) -> Optional[Dict[str, Any]]:
    """认证请求"""
    token = request.headers.get("Authorization")
    if not token:
        return None
    
    # 验证JWT Token
    try:
        # 这里应该调用user-service验证token
        # 简化实现，直接返回用户信息
        return {"user_id": "user123", "roles": ["user"]}
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return None

# 限流中间件
async def check_rate_limit(request: Request, service: str) -> bool:
    """检查限流"""
    client_ip = request.client.host
    user_id = getattr(request.state, 'user_id', client_ip)
    
    limit_config = GATEWAY_CONFIG["rate_limits"].get(
        service, 
        GATEWAY_CONFIG["rate_limits"]["default"]
    )
    
    return await rate_limiter.is_allowed(
        key=f"{service}:{user_id}",
        limit=limit_config["requests"],
        window=limit_config["window"]
    )

# 健康检查
@app.get("/health")
async def health_check():
    """网关健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": GATEWAY_CONFIG["version"]
    }

# 服务发现
@app.get("/services")
async def list_services():
    """列出所有服务"""
    return {
        "services": list(GATEWAY_CONFIG["services"].keys()),
        "gateway_version": GATEWAY_CONFIG["version"]
    }

# 服务状态检查
@app.get("/services/{service_name}/health")
async def check_service_health(service_name: str):
    """检查特定服务健康状态"""
    if service_name not in GATEWAY_CONFIG["services"]:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service_url = GATEWAY_CONFIG["services"][service_name]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{service_url}/health", timeout=5.0)
            return {
                "service": service_name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "service": service_name,
            "status": "unhealthy",
            "error": str(e)
        }

# 代理请求到微服务
@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(authenticate_request)
):
    """代理请求到微服务"""
    
    # 检查服务是否存在
    if service_name not in GATEWAY_CONFIG["services"]:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # 检查限流
    if not await check_rate_limit(request, service_name):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # 获取服务URL
    service_url = GATEWAY_CONFIG["services"][service_name]
    target_url = f"{service_url}/{path}"
    
    # 使用熔断器
    circuit_breaker = circuit_breakers[service_name]
    
    try:
        # 构建请求头
        headers = dict(request.headers)
        headers.pop("host", None)  # 移除host头
        
        # 添加用户信息到请求头
        if user:
            headers["X-User-ID"] = user.get("user_id", "")
            headers["X-User-Roles"] = ",".join(user.get("roles", []))
        
        # 获取请求体
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # 代理请求
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params,
                    timeout=30.0
                )
                return response
        
        # 使用熔断器执行请求
        response = await circuit_breaker.call(make_request)
        
        # 记录请求日志
        logger.info(f"Proxied {request.method} {request.url} -> {target_url} [{response.status_code}]")
        
        # 返回响应
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Proxy request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

# 监控指标
@app.get("/metrics")
async def get_metrics():
    """获取网关监控指标"""
    metrics = {
        "gateway": {
            "requests_total": 0,  # 这里应该从监控系统获取
            "requests_per_second": 0,
            "error_rate": 0,
            "average_response_time": 0
        },
        "services": {}
    }
    
    # 获取各服务指标
    for service_name in GATEWAY_CONFIG["services"]:
        circuit_breaker = circuit_breakers[service_name]
        metrics["services"][service_name] = {
            "circuit_breaker_state": circuit_breaker.state,
            "failure_count": circuit_breaker.failure_count,
            "last_failure_time": circuit_breaker.last_failure_time
        }
    
    return metrics

# 启动事件
@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("API Gateway starting up...")
    
    # 检查Redis连接
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
    
    # 预热服务连接
    for service_name, service_url in GATEWAY_CONFIG["services"].items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                logger.info(f"Service {service_name} is healthy")
        except Exception as e:
            logger.warning(f"Service {service_name} is not available: {e}")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("API Gateway shutting down...")
    await http_client.aclose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

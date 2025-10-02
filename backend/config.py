"""
配置文件
用于生产环境的配置管理
"""
import os
from pathlib import Path
from typing import Optional

class Config:
    """应用配置类"""
    
    # 基础配置
    APP_NAME = "MIL-STD-6016 PDF Processing System"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "milstd6016")
    
    # API配置
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # 文件上传配置
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {".pdf"}
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
    
    # PDF处理配置
    PDF_PROCESSING_TIMEOUT = int(os.getenv("PDF_PROCESSING_TIMEOUT", "300"))  # 5分钟
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "3"))
    MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.7"))
    MAX_BITS = int(os.getenv("MAX_BITS", "70"))
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10")) * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # 安全配置
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-here")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # 缓存配置
    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1小时
    
    # 监控配置
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
    
    # 邮件配置
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    
    # 通知配置
    NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")
    NOTIFICATION_WEBHOOK = os.getenv("NOTIFICATION_WEBHOOK", "")
    
    @classmethod
    def validate_config(cls):
        """验证配置"""
        errors = []
        
        # 检查必需的配置
        if not cls.DB_PASSWORD:
            errors.append("DB_PASSWORD is required")
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == "your-secret-key-here":
            errors.append("SECRET_KEY must be set to a secure value")
        
        # 检查目录
        for dir_name in [cls.UPLOAD_DIR, cls.OUTPUT_DIR, cls.LOG_DIR]:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create directory {dir_name}: {e}")
        
        # 检查文件大小限制
        if cls.MAX_FILE_SIZE <= 0:
            errors.append("MAX_FILE_SIZE must be positive")
        
        if cls.MAX_FILE_SIZE > 100 * 1024 * 1024:  # 100MB
            errors.append("MAX_FILE_SIZE is too large (max 100MB)")
        
        return errors
    
    @classmethod
    def get_database_url(cls) -> str:
        """获取数据库连接URL"""
        return f"mysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_redis_url(cls) -> str:
        """获取Redis连接URL"""
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_WORKERS = 1

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    MAX_WORKERS = 4

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DB_NAME = "milstd6016_test"
    MAX_WORKERS = 1

def get_config() -> Config:
    """根据环境获取配置"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

# 全局配置实例
config = get_config()

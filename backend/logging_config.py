"""
日志配置模块
用于生产环境的日志记录和错误处理
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志目录
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器 - 所有日志
    all_log_file = log_path / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        all_log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 错误日志处理器
    error_log_file = log_path / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # PDF处理专用日志
    pdf_logger = logging.getLogger("pdf_processing")
    pdf_log_file = log_path / "pdf_processing.log"
    pdf_handler = logging.handlers.RotatingFileHandler(
        pdf_log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    pdf_handler.setLevel(logging.INFO)
    pdf_handler.setFormatter(formatter)
    pdf_logger.addHandler(pdf_handler)
    pdf_logger.propagate = False
    
    # 数据库操作日志
    db_logger = logging.getLogger("database")
    db_log_file = log_path / "database.log"
    db_handler = logging.handlers.RotatingFileHandler(
        db_log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(formatter)
    db_logger.addHandler(db_handler)
    db_logger.propagate = False
    
    return root_logger

def log_processing_start(pdf_path: str, user_id: str = None):
    """记录处理开始"""
    logger = logging.getLogger("pdf_processing")
    logger.info(f"PDF处理开始: {pdf_path}, 用户: {user_id or 'anonymous'}")
    logger.info(f"处理时间: {datetime.now().isoformat()}")

def log_processing_end(pdf_path: str, success: bool, result: dict = None, user_id: str = None):
    """记录处理结束"""
    logger = logging.getLogger("pdf_processing")
    status = "成功" if success else "失败"
    logger.info(f"PDF处理{status}: {pdf_path}, 用户: {user_id or 'anonymous'}")
    
    if result:
        logger.info(f"处理结果: J消息={result.get('j_messages', 0)}, 字段={result.get('fields', 0)}")
        if not success and 'error' in result:
            logger.error(f"处理错误: {result['error']}")

def log_database_operation(operation: str, table: str, record_id: str = None, success: bool = True):
    """记录数据库操作"""
    logger = logging.getLogger("database")
    status = "成功" if success else "失败"
    record_info = f", 记录ID: {record_id}" if record_id else ""
    logger.info(f"数据库操作{status}: {operation} -> {table}{record_info}")

def log_validation_result(validation_result: dict, file_path: str):
    """记录校验结果"""
    logger = logging.getLogger("pdf_processing")
    logger.info(f"校验结果: {file_path}")
    logger.info(f"  状态: {'通过' if validation_result.get('valid') else '失败'}")
    logger.info(f"  覆盖率: {validation_result.get('coverage', 0):.2%}")
    logger.info(f"  置信度: {validation_result.get('confidence', 0):.2%}")
    logger.info(f"  错误数: {len(validation_result.get('errors', []))}")
    logger.info(f"  警告数: {len(validation_result.get('warnings', []))}")

def log_batch_processing_start(batch_id: str, file_count: int, user_id: str = None):
    """记录批量处理开始"""
    logger = logging.getLogger("pdf_processing")
    logger.info(f"批量处理开始: ID={batch_id}, 文件数={file_count}, 用户: {user_id or 'anonymous'}")

def log_batch_processing_end(batch_id: str, success_count: int, total_count: int, user_id: str = None):
    """记录批量处理结束"""
    logger = logging.getLogger("pdf_processing")
    logger.info(f"批量处理结束: ID={batch_id}, 成功={success_count}/{total_count}, 用户: {user_id or 'anonymous'}")

def log_api_request(method: str, path: str, user_id: str = None, status_code: int = None):
    """记录API请求"""
    logger = logging.getLogger("api")
    status_info = f", 状态码: {status_code}" if status_code else ""
    logger.info(f"API请求: {method} {path}, 用户: {user_id or 'anonymous'}{status_info}")

def log_security_event(event_type: str, details: str, user_id: str = None, ip_address: str = None):
    """记录安全事件"""
    logger = logging.getLogger("security")
    ip_info = f", IP: {ip_address}" if ip_address else ""
    logger.warning(f"安全事件: {event_type}, 详情: {details}, 用户: {user_id or 'anonymous'}{ip_info}")

def cleanup_old_logs(log_dir: str = "logs", days_to_keep: int = 30):
    """清理旧日志文件"""
    import time
    from pathlib import Path
    
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    
    current_time = time.time()
    cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
    
    for log_file in log_path.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                logging.info(f"删除旧日志文件: {log_file}")
            except Exception as e:
                logging.error(f"删除日志文件失败: {log_file}, 错误: {e}")

# 默认日志配置
def setup_default_logging():
    """设置默认日志配置"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_dir = os.getenv("LOG_DIR", "logs")
    return setup_logging(log_level, log_dir)

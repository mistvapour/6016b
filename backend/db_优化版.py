"""
优化的数据库模块 - 添加连接超时，避免长时间等待
"""
import mysql.connector
import os
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """获取数据库连接，添加超时设置"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "milstd6016"),
            autocommit=True,
            connection_timeout=5,  # 连接超时 5 秒
            connect_timeout=5,      # 连接尝试超时 5 秒
            buffered=True           # 使用缓冲游标
        )
        return conn
    except mysql.connector.Error as e:
        # 连接失败时抛出异常，不阻塞
        raise ConnectionError(f"数据库连接失败: {e}") from e

def query(sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """执行查询，添加超时和错误处理"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    except (mysql.connector.Error, ConnectionError) as e:
        # 连接或查询失败时返回空列表，不阻塞
        print(f"数据库查询失败: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

def call_proc(proc_name: str, params: Optional[Tuple] = None) -> List[List[Dict[str, Any]]]:
    """调用存储过程，添加超时和错误处理"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.callproc(proc_name, params or ())
        results = []
        for result in cursor.stored_results():
            results.append(result.fetchall())
        return results
    except (mysql.connector.Error, ConnectionError) as e:
        # 连接或存储过程调用失败时返回空列表，不阻塞
        print(f"存储过程调用失败: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

def exec_sql(sql: str, params: Optional[Tuple] = None) -> None:
    """执行 SQL 语句，添加超时和错误处理"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
    except (mysql.connector.Error, ConnectionError) as e:
        # 连接或执行失败时记录错误，不阻塞
        print(f"SQL 执行失败: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


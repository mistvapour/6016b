import mysql.connector
import os
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "milstd6016"),
        autocommit=True
    )

def query(sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        conn.close()

def call_proc(proc_name: str, params: Optional[Tuple] = None) -> List[List[Dict[str, Any]]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc(proc_name, params or ())
        results = []
        for result in cursor.stored_results():
            results.append(result.fetchall())
        return results
    finally:
        conn.close()

def exec_sql(sql: str, params: Optional[Tuple] = None) -> None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
    finally:
        conn.close()

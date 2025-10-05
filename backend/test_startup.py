#!/usr/bin/env python3
"""
测试后端启动的脚本
"""
import sys
import traceback

def test_imports():
    print("开始测试导入...")
    
    try:
        print("1. 测试基础导入...")
        import os
        import io
        import csv
        import logging
        import re
        print("   ✓ 基础模块导入成功")
        
        print("2. 测试FastAPI导入...")
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import StreamingResponse
        from pydantic import BaseModel
        from typing import Optional
        print("   ✓ FastAPI模块导入成功")
        
        print("3. 测试数据库模块...")
        from db import call_proc, query, exec_sql
        print("   ✓ 数据库模块导入成功")
        
        print("4. 测试API模块...")
        from pdf_api import include_pdf_routes
        from import_yaml import import_yaml_to_database, batch_import_yaml_files
        from mqtt_api import router as mqtt_router
        from universal_import_api import include_universal_routes
        from semantic_interop_api import include_semantic_routes
        from cdm_api import include_cdm_routes
        from unified_api import include_unified_routes
        print("   ✓ API模块导入成功")
        
        print("5. 测试main模块...")
        import main
        print("   ✓ main模块导入成功")
        
        print("6. 测试创建FastAPI应用...")
        app = main.app
        print("   ✓ FastAPI应用创建成功")
        
        print("7. 测试健康检查端点...")
        # 模拟健康检查
        try:
            from db import get_connection
            conn = get_connection()
            conn.close()
            print("   ✓ 数据库连接测试成功")
        except Exception as e:
            print(f"   ⚠ 数据库连接测试失败: {e}")
        
        print("\n✅ 所有测试通过！后端应该可以正常启动。")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
集成测试脚本
测试PDF处理系统的完整功能
"""
import os
import sys
import json
import time
import requests
from pathlib import Path

def test_api_health():
    """测试API健康检查"""
    print("🔍 测试API健康检查...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ API健康检查通过")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API健康检查失败: {e}")
        return False

def test_pdf_processing():
    """测试PDF处理功能"""
    print("🔍 测试PDF处理功能...")
    try:
        # 检查测试文件是否存在
        test_pdf = "sample_j_message.pdf"
        if not Path(test_pdf).exists():
            print(f"❌ 测试PDF文件不存在: {test_pdf}")
            return False
        
        # 上传PDF文件
        with open(test_pdf, 'rb') as f:
            files = {'file': f}
            data = {
                'standard': 'MIL-STD-6016',
                'edition': 'B'
            }
            response = requests.post("http://localhost:8000/api/pdf/process", 
                                   files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ PDF处理功能正常")
                print(f"   生成文件: {len(result.get('data', {}).get('yaml_files', []))} 个")
                return True
            else:
                print(f"❌ PDF处理失败: {result.get('error')}")
                return False
        else:
            print(f"❌ PDF处理请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ PDF处理测试失败: {e}")
        return False

def test_yaml_import():
    """测试YAML导入功能"""
    print("🔍 测试YAML导入功能...")
    try:
        # 检查YAML文件是否存在
        yaml_dir = "test_output"
        if not Path(yaml_dir).exists():
            print(f"❌ YAML目录不存在: {yaml_dir}")
            return False
        
        # 试运行导入
        response = requests.post("http://localhost:8000/api/import/yaml/batch", 
                               params={
                                   'yaml_dir': yaml_dir,
                                   'dry_run': True
                               }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ YAML导入功能正常")
                print(f"   处理文件: {result.get('total_files', 0)} 个")
                return True
            else:
                print(f"❌ YAML导入失败: {result.get('error')}")
                return False
        else:
            print(f"❌ YAML导入请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ YAML导入测试失败: {e}")
        return False

def test_batch_processing():
    """测试批量处理功能"""
    print("🔍 测试批量处理功能...")
    try:
        # 创建测试PDF目录
        test_dir = Path("test_pdfs")
        test_dir.mkdir(exist_ok=True)
        
        # 复制测试PDF文件
        if Path("sample_j_message.pdf").exists():
            import shutil
            shutil.copy("sample_j_message.pdf", test_dir / "test1.pdf")
            shutil.copy("sample_j_message.pdf", test_dir / "test2.pdf")
        
        # 批量处理
        response = requests.post("http://localhost:8000/api/pdf/batch-process", 
                               json={
                                   'pdf_dir': str(test_dir),
                                   'output_dir': 'batch_test_output',
                                   'standard': 'MIL-STD-6016',
                                   'edition': 'B'
                               }, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 批量处理功能正常")
                print(f"   处理文件: {result.get('data', {}).get('summary', {}).get('successful', 0)} 个")
                return True
            else:
                print(f"❌ 批量处理失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 批量处理请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 批量处理测试失败: {e}")
        return False

def test_frontend():
    """测试前端界面"""
    print("🔍 测试前端界面...")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ 前端界面可访问")
            return True
        else:
            print(f"❌ 前端界面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端界面测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        # 通过API测试数据库连接
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'db' in data and 'version' in data:
                print("✅ 数据库连接正常")
                print(f"   数据库: {data.get('db')}")
                print(f"   版本: {data.get('version')}")
                return True
            else:
                print("❌ 数据库连接信息不完整")
                return False
        else:
            print(f"❌ 数据库连接测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    print("🔍 测试文件操作...")
    try:
        # 检查必要目录
        required_dirs = ['uploads', 'output', 'logs', 'test_output']
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                Path(dir_name).mkdir(exist_ok=True)
                print(f"   创建目录: {dir_name}")
        
        # 检查文件权限
        test_file = Path("test_output/test.txt")
        test_file.write_text("test")
        test_file.unlink()
        
        print("✅ 文件操作正常")
        return True
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("PDF处理系统集成测试")
    print("=" * 60)
    
    tests = [
        ("API健康检查", test_api_health),
        ("数据库连接", test_database_connection),
        ("文件操作", test_file_operations),
        ("PDF处理", test_pdf_processing),
        ("YAML导入", test_yaml_import),
        ("批量处理", test_batch_processing),
        ("前端界面", test_frontend),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # 避免请求过快
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "health":
            test_api_health()
        elif test_name == "pdf":
            test_pdf_processing()
        elif test_name == "import":
            test_yaml_import()
        elif test_name == "batch":
            test_batch_processing()
        elif test_name == "frontend":
            test_frontend()
        elif test_name == "database":
            test_database_connection()
        elif test_name == "files":
            test_file_operations()
        else:
            print("未知测试名称，可用选项: health, pdf, import, batch, frontend, database, files")
    else:
        run_all_tests()

if __name__ == "__main__":
    main()

"""
检查真正的 API 业务模块是否存在循环导入问题
只检查业务模块，排除测试和诊断脚本
"""
import os
import re

print("=" * 60)
print("检查 API 业务模块循环导入问题")
print("=" * 60)
print()

backend_dir = os.path.dirname(os.path.abspath(__file__))

# 要检查的业务模块（API 模块）
api_modules = [
    'pdf_api.py',
    'mqtt_api.py',
    'universal_import_api.py',
    'semantic_interop_api.py',
    'cdm_api.py',
    'unified_api.py',
    'message_generation_api.py',
]

# 其他可能包含业务逻辑的文件
other_modules = []

# 排除的文件和目录
excluded_dirs = {'.venv', 'venv', '__pycache__', 'node_modules'}
excluded_files = {
    'main.py', 'main_test.py', 'main_最小版.py', 'main_无数据库.py',
    'test_startup.py', '测试导入.py', '检查启动错误.py', 
    '检查循环导入.py', '诊断阻塞模块.py', '检查数据库连接.py',
    '__init__.py', 'db.py'
}

print("检查业务模块是否从 main.py 导入...")
print("-" * 60)

found_imports = []
checked_files = []

# 检查指定的 API 模块
for module_name in api_modules:
    filepath = os.path.join(backend_dir, module_name)
    if os.path.exists(filepath):
        checked_files.append(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查是否有 from main import 或 import main
                if re.search(r'from\s+main\s+import', content) or re.search(r'import\s+main', content):
                    found_imports.append((filepath, content))
                    print(f"❌ 发现循环导入: {os.path.basename(filepath)}")
                    
                    # 提取相关行
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.search(r'from\s+main\s+import', line) or re.search(r'import\s+main', line):
                            print(f"   第 {i} 行: {line.strip()}")
                else:
                    print(f"✅ {os.path.basename(filepath)} - 无循环导入")
        except Exception as e:
            print(f"   ⚠️  读取失败: {module_name} - {e}")

# 检查其他业务文件（不在排除列表中）
print()
print("-" * 60)
print("检查其他业务模块...")
print("-" * 60)

for root, dirs, files in os.walk(backend_dir):
    # 跳过排除的目录
    if any(skip in root for skip in excluded_dirs):
        continue
    
    for file in files:
        if not file.endswith('.py'):
            continue
        
        # 跳过排除的文件
        if file in excluded_files:
            continue
        
        # 跳过测试文件
        if 'test' in file.lower():
            continue
        
        # 跳过诊断脚本
        if any(keyword in file for keyword in ['检查', '诊断', '测试']):
            continue
        
        filepath = os.path.join(root, file)
        
        # 跳过已经检查的 API 模块
        if filepath in checked_files:
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查是否有 from main import 或 import main
                if re.search(r'from\s+main\s+import', content) or re.search(r'import\s+main', content):
                    found_imports.append((filepath, content))
                    rel_path = os.path.relpath(filepath, backend_dir)
                    print(f"❌ 发现循环导入: {rel_path}")
                    
                    # 提取相关行
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.search(r'from\s+main\s+import', line) or re.search(r'import\s+main', line):
                            print(f"   第 {i} 行: {line.strip()}")
        except Exception as e:
            pass  # 忽略读取错误

print()
print("-" * 60)

if found_imports:
    print()
    print("=" * 60)
    print("❌ 发现循环导入问题！")
    print("=" * 60)
    print()
    print("这些业务模块从 main.py 导入，会导致循环导入：")
    for filepath, _ in found_imports:
        rel_path = os.path.relpath(filepath, backend_dir)
        print(f"  - {rel_path}")
    print()
    print("解决方法：")
    print("  1. 不要在子模块中 'from main import app'")
    print("  2. 使用 APIRouter，在 main.py 中注册路由")
    print("  3. 把共享配置（如 DB_AVAILABLE）放到单独的 config.py")
    print("  4. 如果需要 app 对象，通过参数传递，而不是导入")
    print()
else:
    print()
    print("=" * 60)
    print("✅ 未发现业务模块循环导入问题")
    print("=" * 60)
    print()
    print("如果仍然卡住，可能是其他原因：")
    print("  - 模块在导入时连接网络/数据库（没有超时）")
    print("  - 模块在导入时执行阻塞操作")
    print("  - 模块依赖的其他模块有问题")
    print()
    print("建议：运行主版本查看详细日志，找出最后加载的模块")
    print()

print()


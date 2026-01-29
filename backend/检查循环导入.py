"""
检查是否存在循环导入问题
"""
import os
import re

print("=" * 60)
print("检查循环导入问题")
print("=" * 60)
print()

backend_dir = os.path.dirname(os.path.abspath(__file__))

# 检查是否有从 main 导入
print("检查是否有模块从 main.py 导入...")
print("-" * 60)

found_imports = []

# 排除的文件和目录（测试文件、诊断脚本等）
excluded_files = {
    'main.py', 'main_test.py', 'main_最小版.py', 'main_无数据库.py',
    'test_startup.py', '测试导入.py', '检查启动错误.py', 
    '检查循环导入.py', '诊断阻塞模块.py', '检查数据库连接.py',
    '__init__.py'
}

for root, dirs, files in os.walk(backend_dir):
    # 跳过虚拟环境、测试目录、缓存目录
    if any(skip in root for skip in ['.venv', 'venv', '__pycache__', 'test', 'tests']):
        continue
    
    for file in files:
        if not file.endswith('.py'):
            continue
        
        # 跳过测试和诊断文件
        if file in excluded_files:
            continue
        
        # 跳过测试文件（文件名包含 test）
        if 'test' in file.lower() and file != '__init__.py':
            continue
        
        # 跳过诊断脚本（文件名包含 检查、诊断、测试）
        if any(keyword in file for keyword in ['检查', '诊断', '测试']):
            continue
        
        filepath = os.path.join(root, file)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查是否有 from main import 或 import main
                if re.search(r'from\s+main\s+import', content) or re.search(r'import\s+main', content):
                    found_imports.append((filepath, content))
                    print(f"⚠️  发现: {filepath}")
                    
                    # 提取相关行
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.search(r'from\s+main\s+import', line) or re.search(r'import\s+main', line):
                            print(f"   第 {i} 行: {line.strip()}")
                    
        except Exception as e:
            print(f"  读取文件失败: {filepath} - {e}")

print()
print("-" * 60)

if found_imports:
    print()
    print("=" * 60)
    print("❌ 发现循环导入问题！")
    print("=" * 60)
    print()
    print("这些文件从 main.py 导入，可能导致循环导入：")
    for filepath, _ in found_imports:
        print(f"  - {filepath}")
    print()
    print("解决方法：")
    print("  1. 不要在子模块中 'from main import app'")
    print("  2. 使用 APIRouter，在 main.py 中注册")
    print("  3. 把共享配置放到单独的 config.py")
    print()
else:
    print()
    print("=" * 60)
    print("✅ 未发现循环导入问题")
    print("=" * 60)
    print()
    print("如果仍然卡住，可能是其他原因：")
    print("  - 模块在导入时连接网络/数据库")
    print("  - 模块在导入时执行阻塞操作")
    print()
    print("建议：查看 main.py 的导入日志，找出最后加载的模块")

print()


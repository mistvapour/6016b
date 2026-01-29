"""
测试数据库连接 - 快速诊断数据库问题
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("数据库连接测试")
print("=" * 60)
print()

# 读取配置
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = int(os.getenv("DB_PORT", "3306"))
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME", "milstd6016")

print(f"数据库配置:")
print(f"  主机: {db_host}")
print(f"  端口: {db_port}")
print(f"  用户: {db_user}")
print(f"  数据库: {db_name}")
print()

# 检查 MySQL 驱动
try:
    import mysql.connector
    print("✓ MySQL 驱动已安装")
except ImportError:
    print("✗ MySQL 驱动未安装")
    print("  请运行: pip install mysql-connector-python")
    sys.exit(1)

print()
print("正在尝试连接数据库（5秒超时）...")
print()

try:
    conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        connection_timeout=5,  # 5秒超时
        connect_timeout=5
    )
    
    print("✓ 数据库连接成功！")
    print()
    
    # 测试查询
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE(), VERSION()")
    db_info = cursor.fetchone()
    print(f"当前数据库: {db_info[0]}")
    print(f"MySQL 版本: {db_info[1]}")
    
    conn.close()
    print()
    print("=" * 60)
    print("✓ 所有测试通过！数据库连接正常")
    print("=" * 60)
    
except mysql.connector.Error as e:
    print()
    print("=" * 60)
    print(f"✗ 数据库连接失败")
    print("=" * 60)
    print(f"错误信息: {e}")
    print()
    print("可能的原因:")
    print("  1. MySQL 服务未启动")
    print("     - 按 Win+R，输入 services.msc")
    print("     - 查找 MySQL 服务并启动")
    print()
    print("  2. 数据库配置错误")
    print("     - 检查 .env 文件中的配置")
    print("     - 确认主机、端口、用户名、密码正确")
    print()
    print("  3. 防火墙阻止连接")
    print("     - 检查防火墙设置")
    print()
    print("建议:")
    print("  - 如果暂时不需要数据库，可以使用 main_无数据库.py")
    print("  - 或者启动 MySQL 服务后再测试")
    print()
    sys.exit(1)

except Exception as e:
    print()
    print("=" * 60)
    print(f"✗ 发生未知错误")
    print("=" * 60)
    print(f"错误信息: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)


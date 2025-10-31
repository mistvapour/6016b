#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Python环境
"""

print("Python环境测试开始...")

try:
    import matplotlib
    print(f"matplotlib版本: {matplotlib.__version__}")
    
    import matplotlib.pyplot as plt
    print("matplotlib.pyplot导入成功")
    
    import numpy as np
    print(f"numpy版本: {np.__version__}")
    
    # 创建一个简单的测试图
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax.set_title('测试图')
    
    # 保存图片
    plt.savefig('test_plot.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("测试图片已保存为 test_plot.png")
    
except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")

print("Python环境测试完成")

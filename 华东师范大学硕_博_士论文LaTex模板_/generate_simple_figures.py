#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用PIL生成第四章跨数据链协议互操作架构设计的三张配图
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 设置图片保存路径
output_dir = "chapters/fig-0"
os.makedirs(output_dir, exist_ok=True)

def create_simple_figure(title, content, filename, width=1200, height=800):
    """创建简单的图片"""
    # 创建白色背景
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体，如果失败则使用默认字体
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        content_font = ImageFont.truetype("arial.ttf", 16)
    except:
        title_font = ImageFont.load_default()
        content_font = ImageFont.load_default()
    
    # 绘制标题
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 50), title, fill='black', font=title_font)
    
    # 绘制内容
    y_offset = 120
    for line in content:
        line_bbox = draw.textbbox((0, 0), line, font=content_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        draw.text((line_x, y_offset), line, fill='black', font=content_font)
        y_offset += 40
    
    # 保存图片
    img.save(os.path.join(output_dir, filename), 'PNG')
    print(f"已生成: {filename}")

def main():
    """主函数"""
    print("开始生成第四章跨数据链协议互操作架构设计配图...")
    
    try:
        # 图1: 多协议支持体系架构图
        print("正在生成图1...")
        title1 = "多协议支持体系架构"
        content1 = [
            "协议层: MIL-STD-6016, MAVLink, MQTT, Link 16",
            "协议适配层: 结构解析与适配 • 消息格式转换 • 统一内部表示",
            "语义抽象层: 统一语义模型 • 概念映射 • 语义理解",
            "转换引擎层: 格式转换 • 单位转换 • 枚举映射 • 转换规则配置",
            "路由分发层: 智能路由 • 负载均衡 • 故障转移"
        ]
        create_simple_figure(title1, content1, "multi_protocol_support_system.png")
        
        # 图2: CDM四层法语义互操作模型图
        print("正在生成图2...")
        title2 = "CDM四层法语义互操作模型"
        content2 = [
            "语义层: 统一本体模型 • 概念推理机制 • 语义关系理解",
            "映射层: 声明式规则映射 • YAML配置化管理 • 版本管理",
            "校验层: 多层次一致性验证 • 金标准回归测试",
            "运行层: 高性能实时转换引擎 • 缓存优化技术"
        ]
        create_simple_figure(title2, content2, "cdm_four_layer_model.png")
        
        # 图3: 语义互操作系统组成图
        print("正在生成图3...")
        title3 = "语义互操作系统组成"
        content3 = [
            "语义注册表: 语义字段管理 • 消息定义管理 • 概念库管理",
            "语义转换器: 字段级数据转换 • 单位转换 • 枚举映射",
            "消息路由器: 智能路由机制 • 协议选择优化 • 转换策略优化",
            "互操作管理器: 跨标准转换管理 • 质量监控 • 性能优化"
        ]
        create_simple_figure(title3, content3, "semantic_interop_system.png")
        
        print("所有配图生成完成！")
        print(f"图片保存在: {output_dir}/")
        
    except Exception as e:
        print(f"生成图片时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成第四章配图 - 版本2
使用多种方法确保图片生成成功
"""

import os
import requests
import base64
import zlib
import time
import urllib.parse
from pathlib import Path
import json

class PlantUMLGenerator:
    def __init__(self):
        self.base_urls = [
            "http://www.plantuml.com/plantuml/png/",
            "https://www.plantuml.com/plantuml/png/",
            "http://plantuml.com/plantuml/png/"
        ]
        self.timeout = 30
        self.retry_count = 3
        
    def encode_plantuml(self, text):
        """将PlantUML文本编码为URL安全的格式"""
        try:
            # 确保文本是UTF-8编码
            if isinstance(text, str):
                text = text.encode('utf-8')
            
            # 压缩文本
            compressed = zlib.compress(text)
            
            # Base64编码
            encoded = base64.b64encode(compressed).decode('ascii')
            
            # 转换为PlantUML URL格式
            encoded = encoded.replace('+', '-').replace('/', '_')
            
            return encoded
        except Exception as e:
            print(f"编码失败: {e}")
            return None
    
    def generate_image(self, plantuml_text, output_file):
        """生成PlantUML图片"""
        print(f"正在生成图片: {output_file}")
        print(f"PlantUML文本长度: {len(plantuml_text)} 字符")
        
        # 编码PlantUML文本
        encoded_text = self.encode_plantuml(plantuml_text)
        if not encoded_text:
            print("❌ 编码失败")
            return False
        
        # 尝试多个URL
        for base_url in self.base_urls:
            url = f"{base_url}{encoded_text}"
            print(f"尝试URL: {base_url}")
            
            for attempt in range(self.retry_count):
                try:
                    print(f"  尝试 {attempt + 1}/{self.retry_count}")
                    
                    # 发送请求
                    response = requests.get(url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        # 检查响应内容
                        if len(response.content) > 1000:  # 确保不是错误页面
                            # 保存图片
                            with open(output_file, 'wb') as f:
                                f.write(response.content)
                            
                            print(f"✅ 成功生成图片: {output_file}")
                            print(f"   图片大小: {len(response.content)} 字节")
                            return True
                        else:
                            print(f"   ⚠️ 响应内容太小，可能是错误页面")
                    else:
                        print(f"   ❌ HTTP状态码: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏰ 请求超时")
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ 网络错误: {e}")
                except Exception as e:
                    print(f"   ❌ 其他错误: {e}")
                
                if attempt < self.retry_count - 1:
                    print(f"   等待2秒后重试...")
                    time.sleep(2)
        
        print(f"❌ 所有尝试都失败了")
        return False

def create_plantuml_content():
    """创建PlantUML文件内容"""
    
    # 多协议支持体系架构图
    multi_protocol_content = """@startuml
!theme plain
skinparam backgroundColor white
skinparam componentStyle rectangle
skinparam linetype ortho

title 多协议支持体系架构图

package "路由分发层" as routing {
    component [智能路由器] as router
    component [负载均衡器] as lb
    component [故障转移] as failover
}

package "转换引擎层" as engine {
    component [格式转换器] as format_converter
    component [单位转换器] as unit_converter
    component [枚举映射器] as enum_mapper
    component [转换规则引擎] as rule_engine
}

package "语义抽象层" as semantic {
    component [统一语义模型] as semantic_model
    component [概念映射机制] as concept_mapping
    component [语义推理引擎] as reasoning_engine
}

package "协议适配层" as adapter {
    component [MIL-STD-6016适配器] as mil6016
    component [MAVLink适配器] as mavlink
    component [MQTT适配器] as mqtt
    component [Link 16适配器] as link16
    component [STANAG 5516适配器] as stanag
}

' 协议数据流
mil6016 --> semantic_model : 协议解析
mavlink --> semantic_model : 协议解析
mqtt --> semantic_model : 协议解析
link16 --> semantic_model : 协议解析
stanag --> semantic_model : 协议解析

' 语义处理流
semantic_model --> concept_mapping : 概念对齐
concept_mapping --> reasoning_engine : 语义推理
reasoning_engine --> format_converter : 转换需求

' 转换处理流
format_converter --> unit_converter : 格式转换
unit_converter --> enum_mapper : 单位转换
enum_mapper --> rule_engine : 枚举映射
rule_engine --> router : 转换完成

' 路由分发流
router --> lb : 消息路由
lb --> failover : 负载均衡
failover --> mil6016 : 故障转移
failover --> mavlink : 故障转移
failover --> mqtt : 故障转移
failover --> link16 : 故障转移
failover --> stanag : 故障转移

note right of semantic_model
  统一语义模型建立跨协议
  的概念空间映射
end note

note right of rule_engine
  转换规则引擎支持
  复杂的数据转换需求
end note

note right of router
  智能路由器根据消息类型
  和协议选择最优路径
end note

@enduml"""

    # CDM四层法语义互操作模型图
    cdm_four_layer_content = """@startuml
!theme plain
skinparam backgroundColor white
skinparam componentStyle rectangle
skinparam linetype ortho

title CDM四层法语义互操作模型图

package "运行层 (Runtime Layer)" as runtime {
    component [实时转换引擎] as realtime_engine
    component [批量处理引擎] as batch_engine
    component [缓存管理器] as cache_manager
    component [性能优化器] as optimizer
}

package "校验层 (Validation Layer)" as validation {
    component [格式校验器] as format_validator
    component [业务规则校验器] as business_validator
    component [一致性校验器] as consistency_validator
    component [金标准回归测试] as regression_test
}

package "映射层 (Mapping Layer)" as mapping {
    component [YAML配置管理器] as yaml_config
    component [字段映射器] as field_mapper
    component [数据类型转换器] as type_converter
    component [单位转换器] as unit_converter
    component [版本管理器] as version_manager
}

package "语义层 (Semantic Layer)" as semantic {
    component [本体模型] as ontology_model
    component [概念推理引擎] as concept_reasoning
    component [语义关系库] as semantic_relations
    component [术语词典] as terminology
}

' 数据流向
semantic --> mapping : 语义概念
mapping --> validation : 映射规则
validation --> runtime : 校验结果
runtime --> semantic : 反馈优化

' 语义层内部关系
ontology_model --> concept_reasoning : 本体推理
concept_reasoning --> semantic_relations : 关系推理
semantic_relations --> terminology : 术语映射
terminology --> ontology_model : 概念定义

' 映射层内部关系
yaml_config --> field_mapper : 配置规则
field_mapper --> type_converter : 字段映射
type_converter --> unit_converter : 类型转换
unit_converter --> version_manager : 单位转换
version_manager --> yaml_config : 版本管理

' 校验层内部关系
format_validator --> business_validator : 格式校验
business_validator --> consistency_validator : 业务校验
consistency_validator --> regression_test : 一致性校验
regression_test --> format_validator : 回归测试

' 运行层内部关系
realtime_engine --> batch_engine : 实时处理
batch_engine --> cache_manager : 批量处理
cache_manager --> optimizer : 缓存管理
optimizer --> realtime_engine : 性能优化

note right of semantic
  语义层建立统一的本体模型
  和概念推理机制
end note

note right of mapping
  映射层采用声明式规则映射
  和YAML配置化管理
end note

note right of validation
  校验层提供多层次的一致性
  验证和金标准回归测试
end note

note right of runtime
  运行层实现高性能实时转换
  引擎和批量处理
end note

@enduml"""

    # 语义互操作系统组成图
    semantic_interop_content = """@startuml
!theme plain
skinparam backgroundColor white
skinparam componentStyle rectangle
skinparam linetype ortho

title 语义互操作系统组成图

package "语义互操作系统" as system {
    
    package "核心组件" as core {
        component [语义注册表] as semantic_registry
        component [语义转换器] as semantic_converter
        component [消息路由器] as message_router
        component [互操作管理器] as interop_manager
    }
    
    package "数据存储" as storage {
        database [语义字段库] as field_db
        database [消息定义库] as message_db
        database [概念库] as concept_db
        database [映射规则库] as mapping_db
    }
    
    package "外部接口" as interfaces {
        component [REST API] as rest_api
        component [gRPC接口] as grpc_api
        component [消息队列接口] as mq_interface
    }
}

' 核心组件关系
semantic_registry --> semantic_converter : 语义信息
semantic_converter --> message_router : 转换结果
message_router --> interop_manager : 路由信息
interop_manager --> semantic_registry : 管理指令

' 数据存储关系
semantic_registry --> field_db : 字段管理
semantic_registry --> message_db : 消息管理
semantic_registry --> concept_db : 概念管理
semantic_converter --> mapping_db : 映射规则

' 外部接口关系
rest_api --> semantic_registry : 查询请求
grpc_api --> semantic_converter : 转换请求
mq_interface --> message_router : 消息路由

' 数据流
field_db --> semantic_converter : 字段定义
message_db --> message_router : 消息定义
concept_db --> semantic_converter : 概念映射
mapping_db --> semantic_converter : 转换规则

' 反馈流
semantic_converter --> field_db : 更新字段
message_router --> message_db : 更新消息
interop_manager --> concept_db : 更新概念
interop_manager --> mapping_db : 更新规则

note right of semantic_registry
  语义注册表管理语义字段、
  消息定义、概念库等核心信息
end note

note right of semantic_converter
  语义转换器实现字段级数据转换、
  单位转换、枚举映射等功能
end note

note right of message_router
  消息路由器基于规则的智能路由
  机制，实现协议选择和转换策略
end note

note right of interop_manager
  互操作管理器统一管理跨标准转换、
  质量监控、性能优化等功能
end note

@enduml"""

    return {
        "multi_protocol_support_system": multi_protocol_content,
        "cdm_four_layer_model": cdm_four_layer_content,
        "semantic_interop_system": semantic_interop_content
    }

def main():
    """主函数"""
    print("=" * 80)
    print("重新生成第四章配图 - 版本2")
    print("=" * 80)
    
    # 创建生成器
    generator = PlantUMLGenerator()
    
    # 获取PlantUML内容
    plantuml_contents = create_plantuml_content()
    
    # 定义输出目录
    figures_dir = Path("chapters/fig-0")
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    total_count = len(plantuml_contents)
    
    for i, (name, content) in enumerate(plantuml_contents.items(), 1):
        print(f"\n[{i}/{total_count}] 处理: {name}")
        print("-" * 60)
        
        # 输出文件路径
        output_file = figures_dir / f"{name}.png"
        
        # 生成图片
        if generator.generate_image(content, output_file):
            success_count += 1
        
        # 添加延迟
        if i < total_count:
            print("等待3秒...")
            time.sleep(3)
    
    print("\n" + "=" * 80)
    print(f"生成完成: {success_count}/{total_count} 张图片成功生成")
    print("=" * 80)
    
    if success_count == total_count:
        print("✅ 所有图片生成成功！")
        print("\n生成的图片文件:")
        for name in plantuml_contents.keys():
            output_file = figures_dir / f"{name}.png"
            if output_file.exists():
                size = output_file.stat().st_size
                print(f"  - {name}.png ({size} 字节)")
    else:
        print("⚠️ 部分图片生成失败")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 稍后重试")
        print("3. 考虑使用本地PlantUML工具")

if __name__ == "__main__":
    main()

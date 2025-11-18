#!/usr/bin/env python3
"""
消息生成功能演示脚本
演示消息实例生成、二进制编码、异常注入等功能
"""
from pathlib import Path
import json
from backend.schema.message_definition import MessageDefinition, MessageField, FieldConstraint
from backend.generators.message_instance_generator import MessageInstanceGenerator, GenerationMode
from backend.generators.anomaly_generator import AnomalyMessageGenerator, AnomalyStrategy
from backend.encoders.binary_encoder import BinaryMessageEncoder, BinaryFormat


def create_sample_message_definition() -> MessageDefinition:
    """创建示例消息定义"""
    return MessageDefinition(
        label="J3.2",
        title="Air Track Message",
        version="6016B",
        fields=[
            MessageField(
                name="Track Number",
                dtype="uint16",
                bits=[0, 15],
                units="",
                description="航迹编号",
                constraint=FieldConstraint(
                    required=True,
                    min_value=0,
                    max_value=65535,
                    enum=None
                )
            ),
            MessageField(
                name="Position Latitude",
                dtype="float",
                bits=[16, 47],
                units="deg",
                description="纬度",
                constraint=FieldConstraint(
                    required=True,
                    min_value=-90.0,
                    max_value=90.0,
                    enum=None
                )
            ),
            MessageField(
                name="Position Longitude",
                dtype="float",
                bits=[48, 79],
                units="deg",
                description="经度",
                constraint=FieldConstraint(
                    required=True,
                    min_value=-180.0,
                    max_value=180.0,
                    enum=None
                )
            ),
            MessageField(
                name="Altitude",
                dtype="uint16",
                bits=[80, 95],
                units="m",
                description="高度",
                constraint=FieldConstraint(
                    required=True,
                    min_value=0,
                    max_value=65535,
                    enum=None
                )
            ),
            MessageField(
                name="Track Status",
                dtype="enum",
                bits=[96, 99],
                units="",
                description="航迹状态",
                constraint=FieldConstraint(
                    required=True,
                    min_value=None,
                    max_value=None,
                    enum=["ACTIVE", "INACTIVE", "LOST", "COASTED"]
                )
            ),
            MessageField(
                name="Speed",
                dtype="uint16",
                bits=[100, 115],
                units="kts",
                description="速度",
                constraint=FieldConstraint(
                    required=True,
                    min_value=0,
                    max_value=65535,
                    enum=None
                )
            ),
        ]
    )


def demo_default_generation():
    """演示默认值生成"""
    print("\n" + "="*60)
    print("📋 演示1: 默认值生成")
    print("="*60)
    
    message_def = create_sample_message_definition()
    generator = MessageInstanceGenerator(mode=GenerationMode.DEFAULT)
    
    instance = generator.generate(message_def, fill_header=True)
    
    print("\n生成的消息实例（默认值）:")
    print(json.dumps(instance, ensure_ascii=False, indent=2))


def demo_random_generation():
    """演示随机值生成"""
    print("\n" + "="*60)
    print("🎲 演示2: 随机值生成")
    print("="*60)
    
    message_def = create_sample_message_definition()
    generator = MessageInstanceGenerator(mode=GenerationMode.RANDOM)
    generator.set_random_seed(42)
    
    instances = generator.generate_batch(message_def, count=3, fill_header=True)
    
    print(f"\n生成 {len(instances)} 个随机消息实例:")
    for i, instance in enumerate(instances, 1):
        print(f"\n实例 {i}:")
        print(json.dumps(instance, ensure_ascii=False, indent=2))


def demo_boundary_generation():
    """演示边界值生成"""
    print("\n" + "="*60)
    print("⚠️  演示3: 边界值生成")
    print("="*60)
    
    message_def = create_sample_message_definition()
    generator = MessageInstanceGenerator(mode=GenerationMode.BOUNDARY)
    
    instances = generator.generate_batch(message_def, count=5, fill_header=True)
    
    print(f"\n生成 {len(instances)} 个边界值消息实例:")
    for i, instance in enumerate(instances, 1):
        print(f"\n实例 {i}:")
        print(json.dumps(instance, ensure_ascii=False, indent=2))


def demo_anomaly_generation():
    """演示异常值生成"""
    print("\n" + "="*60)
    print("❌ 演示4: 异常值生成")
    print("="*60)
    
    message_def = create_sample_message_definition()
    generator = MessageInstanceGenerator(mode=GenerationMode.ANOMALY)
    
    instance = generator.generate(message_def, fill_header=True)
    
    print("\n生成的消息实例（异常值）:")
    print(json.dumps(instance, ensure_ascii=False, indent=2))


def demo_anomaly_injection():
    """演示异常注入"""
    print("\n" + "="*60)
    print("🔧 演示5: 异常注入")
    print("="*60)
    
    message_def = create_sample_message_definition()
    
    # 先生成一个正常实例
    generator = MessageInstanceGenerator(mode=GenerationMode.RANDOM)
    normal_instance = generator.generate(message_def, fill_header=True)
    
    print("\n原始正常实例:")
    print(json.dumps(normal_instance, ensure_ascii=False, indent=2))
    
    # 注入不同类型的异常
    strategies = [
        AnomalyStrategy.MISSING_FIELD,
        AnomalyStrategy.TYPE_MISMATCH,
        AnomalyStrategy.OUT_OF_BOUNDS,
        AnomalyStrategy.BIT_OVERFLOW,
    ]
    
    for strategy in strategies:
        anomaly_generator = AnomalyMessageGenerator(strategy=strategy)
        anomalous_instance = anomaly_generator.inject_anomaly(
            message_def,
            normal_instance.copy(),
            target_field="Track Number"
        )
        
        print(f"\n注入异常 ({strategy.value}):")
        print(json.dumps(anomalous_instance, ensure_ascii=False, indent=2))


def demo_binary_encoding():
    """演示二进制编码"""
    print("\n" + "="*60)
    print("🔢 演示6: 二进制编码")
    print("="*60)
    
    message_def = create_sample_message_definition()
    generator = MessageInstanceGenerator(mode=GenerationMode.RANDOM)
    instance = generator.generate(message_def, fill_header=True)
    
    print("\n原始消息实例:")
    print(json.dumps(instance, ensure_ascii=False, indent=2))
    
    # 测试不同格式的编码
    formats = [
        BinaryFormat.RAW,
        BinaryFormat.TLV,
        BinaryFormat.PROTOBUF,
    ]
    
    for fmt in formats:
        encoder = BinaryMessageEncoder(format_type=fmt, endianness="big")
        binary_data = encoder.encode(message_def, instance, alignment=4)
        
        print(f"\n{fmt.value} 格式编码:")
        print(f"  大小: {len(binary_data)} 字节")
        print(f"  十六进制: {binary_data.hex()}")
        print(f"  前32字节: {binary_data[:32].hex()}")


def demo_complete_workflow():
    """演示完整工作流程"""
    print("\n" + "="*60)
    print("🔄 演示7: 完整工作流程")
    print("="*60)
    
    # 1. 创建消息定义
    message_def = create_sample_message_definition()
    print("\n1. 消息定义:")
    print(f"   标签: {message_def.label}")
    print(f"   标题: {message_def.title}")
    print(f"   字段数: {len(message_def.fields)}")
    
    # 2. 生成随机实例
    generator = MessageInstanceGenerator(mode=GenerationMode.RANDOM)
    instance = generator.generate(message_def, fill_header=True)
    print("\n2. 生成的随机实例:")
    print(json.dumps(instance, ensure_ascii=False, indent=2))
    
    # 3. 编码为二进制
    encoder = BinaryMessageEncoder(format_type=BinaryFormat.RAW, endianness="big")
    binary_data = encoder.encode(message_def, instance, alignment=4)
    print(f"\n3. 二进制编码:")
    print(f"   大小: {len(binary_data)} 字节")
    
    # 4. 解码回实例
    decoded_instance = encoder.decode(message_def, binary_data)
    print("\n4. 解码后的实例:")
    print(json.dumps(decoded_instance, ensure_ascii=False, indent=2))
    
    # 5. 生成异常实例用于测试
    anomaly_generator = AnomalyMessageGenerator(strategy=AnomalyStrategy.TYPE_MISMATCH)
    anomalous_instance = anomaly_generator.inject_anomaly(message_def, instance.copy())
    print("\n5. 异常注入后的实例:")
    print(json.dumps(anomalous_instance, ensure_ascii=False, indent=2))


def main():
    """主函数"""
    print("="*60)
    print("🚀 消息生成功能演示")
    print("="*60)
    
    try:
        demo_default_generation()
        demo_random_generation()
        demo_boundary_generation()
        demo_anomaly_generation()
        demo_anomaly_injection()
        demo_binary_encoding()
        demo_complete_workflow()
        
        print("\n" + "="*60)
        print("✅ 所有演示完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


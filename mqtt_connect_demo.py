#!/usr/bin/env python3
"""
模拟MQTT CONNECT PDF处理结果演示
基于test_sample/mqtt_connect_test.pdf的处理
"""
import json
import yaml
from pathlib import Path
from datetime import datetime

def create_mqtt_connect_sim():
    """创建MQTT CONNECT报文的SIM数据"""
    return {
        "standard": "OASIS MQTT",
        "edition": "5.0",
        "transport_unit": "byte",
        "enums": [
            {
                "key": "mqtt_connect_flags",
                "items": [
                    {"code": "0", "label": "Clean Start", "description": "Clean Start flag"},
                    {"code": "1", "label": "Will Flag", "description": "Will Message flag"},
                    {"code": "2", "label": "Will QoS", "description": "Will QoS level"},
                    {"code": "3", "label": "Will Retain", "description": "Will Retain flag"},
                    {"code": "4", "label": "Password Flag", "description": "Password present flag"},
                    {"code": "5", "label": "User Name Flag", "description": "User Name present flag"}
                ]
            },
            {
                "key": "mqtt_qos",
                "items": [
                    {"code": "0", "label": "At most once", "description": "Fire and forget"},
                    {"code": "1", "label": "At least once", "description": "Acknowledged delivery"},
                    {"code": "2", "label": "Exactly once", "description": "Assured delivery"}
                ]
            }
        ],
        "spec_messages": [
            {
                "label": "CONNECT",
                "title": "Connect Packet",
                "transport_unit": "byte",
                "segments": [
                    {
                        "type": "Fixed Header",
                        "seg_idx": 0,
                        "description": "MQTT Control Packet Fixed Header",
                        "fields": [
                            {
                                "name": "MQTT Control Packet Type",
                                "length": 1,
                                "offset": 0,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "bits 7-4: MQTT Control Packet Type (1), bits 3-0: Flags specific to each MQTT Control Packet type",
                                "bit_fields": [
                                    {"name": "Packet Type", "bits": [4, 7], "value": "0001"},
                                    {"name": "Reserved", "bits": [0, 3], "value": "0000"}
                                ]
                            },
                            {
                                "name": "Remaining Length",
                                "length": None,
                                "offset": 1,
                                "offset_unit": "byte",
                                "encoding": "VBI",
                                "description": "Variable Byte Integer representing the number of bytes remaining within the current packet"
                            }
                        ]
                    },
                    {
                        "type": "Variable Header",
                        "seg_idx": 1,
                        "description": "CONNECT Variable Header",
                        "fields": [
                            {
                                "name": "Protocol Name",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded String containing the Protocol Name (MQTT)",
                                "sub_fields": [
                                    {"name": "Length MSB", "length": 1, "encoding": "UINT"},
                                    {"name": "Length LSB", "length": 1, "encoding": "UINT"},
                                    {"name": "Protocol Name", "length": 4, "encoding": "UTF8", "value": "MQTT"}
                                ]
                            },
                            {
                                "name": "Protocol Version",
                                "length": 1,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "The value of the Protocol Version field for MQTT v5.0 is 5 (0x05)",
                                "value": "5"
                            },
                            {
                                "name": "Connect Flags",
                                "length": 1,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "The Connect Flags byte contains several parameters specifying the behavior of the MQTT connection",
                                "bit_fields": [
                                    {"name": "User Name Flag", "bits": [7, 7], "description": "If set to 1, a User Name MUST be present in the Payload"},
                                    {"name": "Password Flag", "bits": [6, 6], "description": "If set to 1, a Password MUST be present in the Payload"},
                                    {"name": "Will Retain", "bits": [5, 5], "description": "Specifies if the Will Message is to be retained when published"},
                                    {"name": "Will QoS", "bits": [3, 4], "description": "Specifies the QoS level to be used when publishing the Will Message"},
                                    {"name": "Will Flag", "bits": [2, 2], "description": "If set to 1, indicates that a Will Message MUST be stored on the Server"},
                                    {"name": "Clean Start", "bits": [1, 1], "description": "Specifies whether the Connection starts with a clean Session"},
                                    {"name": "Reserved", "bits": [0, 0], "description": "Reserved bit, MUST be set to 0"}
                                ]
                            },
                            {
                                "name": "Keep Alive",
                                "length": 2,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Two Byte Integer representing the Keep Alive time period in seconds",
                                "sub_fields": [
                                    {"name": "Keep Alive MSB", "length": 1, "encoding": "UINT"},
                                    {"name": "Keep Alive LSB", "length": 1, "encoding": "UINT"}
                                ]
                            }
                        ]
                    },
                    {
                        "type": "Properties",
                        "seg_idx": 2,
                        "description": "CONNECT Properties",
                        "fields": [
                            {
                                "name": "Property Length",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "VBI",
                                "description": "Variable Byte Integer representing the length of Properties"
                            },
                            {
                                "name": "Session Expiry Interval",
                                "length": 4,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Four Byte Integer representing the Session Expiry Interval in seconds",
                                "property_id": "0x11"
                            },
                            {
                                "name": "Receive Maximum",
                                "length": 2,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Two Byte Integer representing the maximum number of QoS 1 and QoS 2 publications",
                                "property_id": "0x21"
                            },
                            {
                                "name": "Maximum Packet Size",
                                "length": 4,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Four Byte Integer representing the Maximum Packet Size the Client is willing to accept",
                                "property_id": "0x27"
                            },
                            {
                                "name": "Topic Alias Maximum",
                                "length": 2,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Two Byte Integer representing the highest value that the Client will accept as a Topic Alias",
                                "property_id": "0x22"
                            },
                            {
                                "name": "Request Response Information",
                                "length": 1,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Byte indicating whether the Client requests Response Information",
                                "property_id": "0x19"
                            },
                            {
                                "name": "Request Problem Information",
                                "length": 1,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Byte indicating whether the Client requests Problem Information",
                                "property_id": "0x17"
                            },
                            {
                                "name": "User Property",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 String Pair representing User defined name-value pairs",
                                "property_id": "0x26"
                            },
                            {
                                "name": "Authentication Method",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded String containing the name of the authentication method",
                                "property_id": "0x15"
                            },
                            {
                                "name": "Authentication Data",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "BIN",
                                "description": "Binary Data containing authentication data",
                                "property_id": "0x16"
                            }
                        ]
                    },
                    {
                        "type": "Payload",
                        "seg_idx": 3,
                        "description": "CONNECT Payload",
                        "fields": [
                            {
                                "name": "Client Identifier",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded String that identifies the Client to the Server. MUST be present",
                                "required": True
                            },
                            {
                                "name": "Will Properties",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "VBI",
                                "description": "Properties for the Will Message (present if Will Flag is set)",
                                "conditional": "Will Flag = 1"
                            },
                            {
                                "name": "Will Topic",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded String specifying the Will Topic (present if Will Flag is set)",
                                "conditional": "Will Flag = 1"
                            },
                            {
                                "name": "Will Payload",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "BIN",
                                "description": "Binary Data specifying the Will Message Payload (present if Will Flag is set)",
                                "conditional": "Will Flag = 1"
                            },
                            {
                                "name": "User Name",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded String containing the User Name (present if User Name Flag is set)",
                                "conditional": "User Name Flag = 1"
                            },
                            {
                                "name": "Password",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "BIN",
                                "description": "Binary Data containing the Password (present if Password Flag is set)",
                                "conditional": "Password Flag = 1"
                            }
                        ]
                    }
                ],
                "pages": [1, 2, 3],
                "field_count": 25,
                "total_length": "Variable",
                "description": "The CONNECT packet is the first packet sent from the Client to the Server when a network connection is established"
            }
        ],
        "metadata": {
            "source_file": "test_sample/mqtt_connect_test.pdf",
            "processing_date": datetime.now().isoformat(),
            "sections_count": 1,
            "messages_count": 1,
            "total_fields": 25,
            "processor": "mqtt_pdf_adapter",
            "confidence": 0.92,
            "coverage": 0.95
        }
    }

def create_mqtt_connect_output():
    """创建MQTT CONNECT处理输出文件"""
    print("🚀 创建MQTT CONNECT PDF处理结果演示")
    print("=" * 50)
    
    # 创建输出目录
    output_dir = Path("mqtt_connect_output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建SIM数据
    sim = create_mqtt_connect_sim()
    
    # 1. 导出主YAML文件
    main_yaml = output_dir / "mqtt_connect_complete.yaml"
    with open(main_yaml, 'w', encoding='utf-8') as f:
        yaml.safe_dump(sim, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
    
    print(f"✅ 创建主YAML文件: {main_yaml} ({main_yaml.stat().st_size} bytes)")
    
    # 2. 导出JSON格式
    main_json = output_dir / "mqtt_connect_complete.json"
    with open(main_json, 'w', encoding='utf-8') as f:
        json.dump(sim, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建JSON文件: {main_json} ({main_json.stat().st_size} bytes)")
    
    # 3. 创建CONNECT消息单独文件
    connect_msg = sim['spec_messages'][0]
    connect_yaml = output_dir / "connect_message.yaml"
    
    connect_data = {
        'standard': sim['standard'],
        'edition': sim['edition'],
        'message': connect_msg,
        'relevant_enums': sim['enums']
    }
    
    with open(connect_yaml, 'w', encoding='utf-8') as f:
        yaml.safe_dump(connect_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
    
    print(f"✅ 创建CONNECT消息文件: {connect_yaml} ({connect_yaml.stat().st_size} bytes)")
    
    # 4. 创建枚举文件
    enums_file = output_dir / "mqtt_connect_enums.yaml"
    enums_data = {
        'standard': sim['standard'],
        'edition': sim['edition'],
        'enums': sim['enums']
    }
    
    with open(enums_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(enums_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
    
    print(f"✅ 创建枚举文件: {enums_file} ({enums_file.stat().st_size} bytes)")
    
    # 5. 创建处理报告
    report_file = output_dir / "connect_processing_report.json"
    report = {
        'processing_summary': {
            'pdf_filename': 'mqtt_connect_test.pdf',
            'source_path': 'test_sample/mqtt_connect_test.pdf',
            'pages_processed': 3,
            'sections_found': 1,
            'tables_extracted': 2,
            'messages_created': 1,
            'total_fields': 25,
            'processing_time': '12.3 seconds',
            'confidence': 0.92,
            'coverage': 0.95
        },
        'mqtt_connect_details': {
            'packet_type': 'CONNECT',
            'packet_type_code': 1,
            'segments': [
                {
                    'type': 'Fixed Header',
                    'fields': 2,
                    'description': 'MQTT Control Packet Type and Remaining Length'
                },
                {
                    'type': 'Variable Header',
                    'fields': 4,
                    'description': 'Protocol Name, Version, Connect Flags, Keep Alive'
                },
                {
                    'type': 'Properties',
                    'fields': 10,
                    'description': 'MQTT v5.0 Properties for CONNECT packet'
                },
                {
                    'type': 'Payload',
                    'fields': 6,
                    'description': 'Client ID, Will properties, User credentials'
                }
            ]
        },
        'field_analysis': {
            'fixed_length_fields': 8,
            'variable_length_fields': 17,
            'required_fields': 3,
            'conditional_fields': 8,
            'bit_fields': 7,
            'encoding_types': {
                'UINT': 10,
                'UTF8': 8,
                'VBI': 4,
                'BIN': 3
            }
        },
        'validation_results': {
            'structure_valid': True,
            'encoding_consistent': True,
            'mqtt_spec_compliant': True,
            'warnings': [
                "Some conditional fields may require runtime validation",
                "Property IDs should be validated against MQTT v5.0 specification"
            ],
            'errors': []
        },
        'files_generated': [
            'mqtt_connect_complete.yaml',
            'mqtt_connect_complete.json',
            'connect_message.yaml',
            'mqtt_connect_enums.yaml',
            'connect_processing_report.json'
        ]
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建处理报告: {report_file} ({report_file.stat().st_size} bytes)")
    
    # 6. 创建字段映射文件
    field_mapping = output_dir / "connect_field_mapping.yaml"
    mapping_data = {
        'mqtt_connect_field_mapping': {
            'packet_info': {
                'name': 'CONNECT',
                'type_code': 1,
                'direction': 'Client to Server',
                'description': 'Connection request packet'
            },
            'field_mapping': []
        }
    }
    
    # 展平所有字段用于映射
    field_id = 1
    for segment in connect_msg['segments']:
        for field in segment['fields']:
            mapping_entry = {
                'field_id': field_id,
                'segment': segment['type'],
                'name': field['name'],
                'encoding': field['encoding'],
                'length': field.get('length'),
                'required': field.get('required', False),
                'conditional': field.get('conditional'),
                'description': field['description']
            }
            
            # 添加位字段信息
            if 'bit_fields' in field:
                mapping_entry['bit_fields'] = field['bit_fields']
            
            # 添加子字段信息
            if 'sub_fields' in field:
                mapping_entry['sub_fields'] = field['sub_fields']
            
            mapping_data['mqtt_connect_field_mapping']['field_mapping'].append(mapping_entry)
            field_id += 1
    
    with open(field_mapping, 'w', encoding='utf-8') as f:
        yaml.safe_dump(mapping_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
    
    print(f"✅ 创建字段映射文件: {field_mapping} ({field_mapping.stat().st_size} bytes)")
    
    # 显示统计信息
    print("\n📊 MQTT CONNECT处理统计:")
    print(f"   📄 源文件: {sim['metadata']['source_file']}")
    print(f"   📋 标准: {sim['standard']} v{sim['edition']}")
    print(f"   📦 消息: {sim['metadata']['messages_count']} (CONNECT)")
    print(f"   🔧 总字段: {sim['metadata']['total_fields']}")
    print(f"   🏷️  枚举: {len(sim['enums'])}")
    print(f"   📏 置信度: {sim['metadata']['confidence']:.1%}")
    print(f"   📊 覆盖率: {sim['metadata']['coverage']:.1%}")
    
    print("\n📋 CONNECT报文结构:")
    connect_message = sim['spec_messages'][0]
    for segment in connect_message['segments']:
        print(f"   🔸 {segment['type']}: {len(segment['fields'])} 字段")
        for field in segment['fields'][:3]:  # 显示前3个字段
            length_str = f"{field['length']} bytes" if field.get('length') else "Variable"
            print(f"     - {field['name']} ({field['encoding']}, {length_str})")
        if len(segment['fields']) > 3:
            print(f"     ... 还有 {len(segment['fields']) - 3} 个字段")
    
    print("\n📁 生成的文件:")
    for file in output_dir.glob("*"):
        if file.is_file():
            print(f"   📄 {file.name} ({file.stat().st_size} bytes)")
    
    print("\n🔧 数据库导入命令:")
    print(f'   curl -X POST "http://localhost:8000/api/import/yaml?yaml_path={main_yaml}&dry_run=true"')
    
    print("\n✨ MQTT CONNECT PDF处理演示完成！")
    print(f"📁 输出目录: {output_dir}")
    
    return output_dir

def main():
    """主函数"""
    try:
        output_dir = create_mqtt_connect_output()
        print(f"\n🎯 演示文件已生成到: {output_dir}")
        print("您可以使用这些文件测试MQTT PDF处理流水线的功能。")
    except Exception as e:
        print(f"❌ 演示创建失败: {e}")

if __name__ == "__main__":
    main()

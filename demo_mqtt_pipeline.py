#!/usr/bin/env python3
"""
MQTT PDF处理流水线演示
创建模拟数据展示完整流程
"""
import json
import yaml
from pathlib import Path
from datetime import datetime

def create_mock_sim():
    """创建模拟的MQTT SIM数据"""
    return {
        "standard": "OASIS MQTT",
        "edition": "5.0",
        "transport_unit": "byte",
        "enums": [
            {
                "key": "mqtt_qos",
                "items": [
                    {"code": "0", "label": "At most once", "description": "Fire and forget"},
                    {"code": "1", "label": "At least once", "description": "Acknowledged delivery"},
                    {"code": "2", "label": "Exactly once", "description": "Assured delivery"}
                ]
            },
            {
                "key": "mqtt_packet_type",
                "items": [
                    {"code": "1", "label": "CONNECT", "description": "Client request to connect to Server"},
                    {"code": "2", "label": "CONNACK", "description": "Connect acknowledgment"},
                    {"code": "3", "label": "PUBLISH", "description": "Publish message"},
                    {"code": "8", "label": "SUBSCRIBE", "description": "Client subscribe request"}
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
                        "fields": [
                            {
                                "name": "Packet Type",
                                "length": 1,
                                "offset": 0,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "MQTT Control Packet Type"
                            },
                            {
                                "name": "Remaining Length",
                                "length": None,
                                "offset": 1,
                                "offset_unit": "byte", 
                                "encoding": "VBI",
                                "description": "Variable Byte Integer"
                            }
                        ]
                    },
                    {
                        "type": "Variable Header",
                        "seg_idx": 1,
                        "fields": [
                            {
                                "name": "Protocol Name",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded Protocol Name"
                            },
                            {
                                "name": "Protocol Version",
                                "length": 1,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Protocol Version Number"
                            },
                            {
                                "name": "Connect Flags", 
                                "length": 1,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Connect Flags Byte"
                            },
                            {
                                "name": "Keep Alive",
                                "length": 2,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Keep Alive Timer"
                            }
                        ]
                    },
                    {
                        "type": "Properties",
                        "seg_idx": 2,
                        "fields": [
                            {
                                "name": "Property Length",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "VBI",
                                "description": "Variable Byte Integer"
                            },
                            {
                                "name": "Session Expiry Interval",
                                "length": 4,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Four Byte Integer"
                            }
                        ]
                    },
                    {
                        "type": "Payload",
                        "seg_idx": 3,
                        "fields": [
                            {
                                "name": "Client Identifier",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded Client ID"
                            },
                            {
                                "name": "User Name",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded User Name"
                            },
                            {
                                "name": "Password",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "BIN",
                                "description": "Binary Password Data"
                            }
                        ]
                    }
                ],
                "pages": [15, 16, 17],
                "field_count": 10
            },
            {
                "label": "PUBLISH",
                "title": "Publish Packet",
                "transport_unit": "byte",
                "segments": [
                    {
                        "type": "Fixed Header",
                        "seg_idx": 0,
                        "fields": [
                            {
                                "name": "Packet Type",
                                "length": 1,
                                "offset": 0,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "MQTT Control Packet Type"
                            },
                            {
                                "name": "Remaining Length",
                                "length": None,
                                "offset": 1,
                                "offset_unit": "byte",
                                "encoding": "VBI", 
                                "description": "Variable Byte Integer"
                            }
                        ]
                    },
                    {
                        "type": "Variable Header",
                        "seg_idx": 1,
                        "fields": [
                            {
                                "name": "Topic Name",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UTF8",
                                "description": "UTF-8 Encoded Topic Name"
                            },
                            {
                                "name": "Packet Identifier",
                                "length": 2,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "UINT",
                                "description": "Two Byte Integer"
                            }
                        ]
                    },
                    {
                        "type": "Payload",
                        "seg_idx": 2,
                        "fields": [
                            {
                                "name": "Application Message",
                                "length": None,
                                "offset": None,
                                "offset_unit": "byte",
                                "encoding": "BIN",
                                "description": "Binary Application Data"
                            }
                        ]
                    }
                ],
                "pages": [25, 26],
                "field_count": 5
            }
        ],
        "metadata": {
            "sections_count": 2,
            "messages_count": 2,
            "total_fields": 15,
            "processor": "mqtt_pdf_adapter",
            "created_at": datetime.now().isoformat()
        }
    }

def create_demo_files():
    """创建演示文件"""
    print("🚀 创建MQTT PDF处理流水线演示")
    print("=" * 50)
    
    # 创建输出目录
    output_dir = Path("mqtt_demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建模拟SIM数据
    sim = create_mock_sim()
    
    # 1. 导出完整YAML
    main_yaml = output_dir / "mqtt_v5_complete.yaml"
    with open(main_yaml, 'w', encoding='utf-8') as f:
        yaml.safe_dump(sim, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
    
    print(f"✅ 创建主YAML文件: {main_yaml} ({main_yaml.stat().st_size} bytes)")
    
    # 2. 导出JSON格式
    main_json = output_dir / "mqtt_v5_complete.json"
    with open(main_json, 'w', encoding='utf-8') as f:
        json.dump(sim, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建JSON文件: {main_json} ({main_json.stat().st_size} bytes)")
    
    # 3. 创建单独的消息文件
    messages_dir = output_dir / "messages"
    messages_dir.mkdir(exist_ok=True)
    
    for message in sim['spec_messages']:
        label = message['label'].lower()
        message_file = messages_dir / f"{label}_message.yaml"
        
        message_yaml = {
            'standard': sim['standard'],
            'edition': sim['edition'],
            'message': message,
            'relevant_enums': [e for e in sim['enums'] if 'packet' in e['key'] or 'qos' in e['key']]
        }
        
        with open(message_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(message_yaml, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
        
        print(f"✅ 创建{message['label']}消息文件: {message_file} ({message_file.stat().st_size} bytes)")
    
    # 4. 创建枚举文件
    enums_file = output_dir / "mqtt_enums.yaml"
    enums_data = {
        'standard': sim['standard'],
        'edition': sim['edition'],
        'enums': sim['enums']
    }
    
    with open(enums_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(enums_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
    
    print(f"✅ 创建枚举文件: {enums_file} ({enums_file.stat().st_size} bytes)")
    
    # 5. 创建导入清单
    manifest_file = output_dir / "import_manifest.yaml"
    manifest = {
        'metadata': {
            'standard': sim['standard'],
            'edition': sim['edition'],
            'created_at': datetime.now().isoformat(),
            'processor': 'mqtt_pdf_adapter_demo'
        },
        'statistics': {
            'total_messages': len(sim['spec_messages']),
            'total_enums': len(sim['enums']),
            'total_fields': sim['metadata']['total_fields']
        },
        'files': [
            {
                'path': str(f.relative_to(output_dir)),
                'type': 'yaml',
                'description': f"MQTT {f.stem.replace('_message', '').upper()} message definition"
            }
            for f in messages_dir.glob("*.yaml")
        ]
    }
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(manifest, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
    
    print(f"✅ 创建导入清单: {manifest_file} ({manifest_file.stat().st_size} bytes)")
    
    # 6. 创建处理报告
    report_file = output_dir / "processing_report.json"
    report = {
        'processing_summary': {
            'pdf_filename': 'mqtt-v5.0-import.pdf (模拟)',
            'pages_processed': 30,
            'sections_found': 2,
            'tables_extracted': 4,
            'messages_created': 2,
            'total_fields': 15,
            'processing_time': '45.2 seconds',
            'confidence': 0.89
        },
        'messages': [
            {
                'label': msg['label'],
                'segments': len(msg['segments']),
                'fields': msg['field_count'],
                'pages': msg['pages']
            }
            for msg in sim['spec_messages']
        ],
        'validation': {
            'errors': [],
            'warnings': [
                "Some variable length fields lack specific byte constraints",
                "Properties section may need additional validation rules"
            ],
            'coverage': 0.92
        },
        'files_generated': [
            str(f.relative_to(output_dir)) for f in output_dir.rglob("*.yaml")
        ] + [str(f.relative_to(output_dir)) for f in output_dir.rglob("*.json")]
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建处理报告: {report_file} ({report_file.stat().st_size} bytes)")
    
    # 显示统计信息
    print("\n📊 处理统计:")
    print(f"   - 标准: {sim['standard']} v{sim['edition']}")
    print(f"   - 消息数量: {len(sim['spec_messages'])}")
    print(f"   - 总字段数: {sim['metadata']['total_fields']}")
    print(f"   - 枚举数量: {len(sim['enums'])}")
    
    print("\n📁 生成的文件:")
    for file in output_dir.rglob("*"):
        if file.is_file():
            print(f"   - {file.relative_to(output_dir)} ({file.stat().st_size} bytes)")
    
    print("\n📋 消息详情:")
    for message in sim['spec_messages']:
        print(f"   📦 {message['label']} ({message['field_count']} 字段):")
        for segment in message['segments']:
            print(f"     - {segment['type']}: {len(segment['fields'])} 字段")
    
    print("\n🔧 API使用示例:")
    print("1. PDF转YAML:")
    print('   curl -X POST "http://localhost:8000/api/mqtt/pdf_to_yaml?pages=10-50" \\')
    print('        -F "file=@mqtt-v5.0.pdf"')
    
    print("\n2. 完整流水线:")
    print('   curl -X POST "http://localhost:8000/api/mqtt/complete_pipeline?import_to_db=true&dry_run=true" \\')
    print('        -F "file=@mqtt-v5.0.pdf"')
    
    print("\n3. YAML导入数据库:")
    print(f'   curl -X POST "http://localhost:8000/api/import/yaml?yaml_path={main_yaml}&dry_run=true"')
    
    print("\n✨ 演示完成！生成的文件可以直接用于测试导入功能。")
    
    return output_dir

def main():
    """主函数"""
    try:
        output_dir = create_demo_files()
        print(f"\n🎯 演示文件已生成到: {output_dir}")
        print("您可以使用这些文件测试MQTT PDF处理流水线的各个功能。")
    except Exception as e:
        print(f"❌ 演示创建失败: {e}")

if __name__ == "__main__":
    main()

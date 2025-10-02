#!/usr/bin/env python3
"""
统一多格式导入系统演示
展示如何同时处理PDF、XML、JSON、CSV等多种格式文件
"""
import os
import json
from pathlib import Path
from datetime import datetime

def create_demo_files():
    """创建演示用的各种格式文件"""
    demo_dir = "universal_demo_files"
    os.makedirs(demo_dir, exist_ok=True)
    
    # 1. 创建示例JSON文件（协议定义）
    json_data = {
        "standard": "Demo Protocol",
        "edition": "1.0",
        "spec_messages": [
            {
                "label": "DEMO_MESSAGE",
                "title": "Demo Message",
                "message_id": 100,
                "description": "A demonstration message",
                "segments": [
                    {
                        "type": "Header",
                        "seg_idx": 0,
                        "fields": [
                            {
                                "name": "msg_type",
                                "length": 1,
                                "offset_unit": "byte",
                                "description": "Message type identifier"
                            },
                            {
                                "name": "payload_length",
                                "length": 2,
                                "offset_unit": "byte", 
                                "description": "Payload length in bytes"
                            }
                        ]
                    }
                ]
            }
        ],
        "enums": [
            {
                "key": "demo_status",
                "items": [
                    {"code": "0", "label": "OK", "description": "Success"},
                    {"code": "1", "label": "ERROR", "description": "Error occurred"},
                    {"code": "2", "label": "PENDING", "description": "Operation pending"}
                ]
            }
        ]
    }
    
    json_path = os.path.join(demo_dir, "demo_protocol.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # 2. 创建示例XML文件（简化的协议定义）
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<protocol name="Simple Demo Protocol" version="2.0">
    <metadata>
        <author>Demo System</author>
        <created>2024-10-02</created>
        <description>A simple demonstration protocol</description>
    </metadata>
    
    <messages>
        <message id="200" name="SIMPLE_MSG">
            <description>Simple demonstration message</description>
            <fields>
                <field name="header" type="uint8" description="Message header"/>
                <field name="data" type="uint32" description="Message data"/>
                <field name="checksum" type="uint16" description="Message checksum"/>
            </fields>
        </message>
    </messages>
    
    <enums>
        <enum name="message_types">
            <entry value="1" name="DATA_MSG" description="Data message"/>
            <entry value="2" name="CONTROL_MSG" description="Control message"/>
            <entry value="3" name="STATUS_MSG" description="Status message"/>
        </enum>
    </enums>
</protocol>"""
    
    xml_path = os.path.join(demo_dir, "demo_protocol.xml")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    # 3. 创建示例CSV文件（字段定义）
    csv_content = """message,field,bits,description,type,units
DEMO_MSG,msg_id,8,Message identifier,uint8,
DEMO_MSG,timestamp,32,Message timestamp,uint32,ms
DEMO_MSG,sender_id,16,Sender identifier,uint16,
DEMO_MSG,payload,variable,Message payload,bytes,
STATUS_MSG,status_code,8,Status code,uint8,
STATUS_MSG,error_msg,256,Error message,string,chars"""
    
    csv_path = os.path.join(demo_dir, "demo_fields.csv")
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    # 4. 创建已知的测试文件列表
    test_files = [
        "test_sample/common.xml",  # MAVLink XML
        "test_sample/mqtt_connect_test.pdf",  # MQTT PDF
        "test_sample/link16-import.pdf"  # Link 16 PDF
    ]
    
    return {
        "demo_files": [json_path, xml_path, csv_path],
        "existing_test_files": [f for f in test_files if os.path.exists(f)],
        "demo_directory": demo_dir
    }

def generate_processing_report():
    """生成统一导入系统的演示报告"""
    
    # 创建演示文件
    file_info = create_demo_files()
    
    report = {
        "universal_import_demo": {
            "timestamp": datetime.now().isoformat(),
            "system_name": "统一多格式自动化导入系统",
            "version": "1.0.0",
            "description": "支持PDF、XML、JSON、CSV等多种格式的自动识别、转换和导入"
        },
        
        "supported_formats": {
            "PDF": {
                "adapter": "PDFAdapter",
                "standards": ["MIL-STD-6016", "MQTT", "Generic"],
                "features": [
                    "自动标准检测",
                    "专用处理器路由",
                    "大文件分批处理",
                    "表格自动提取"
                ],
                "examples": ["link16-import.pdf", "mqtt_connect_test.pdf"]
            },
            "XML": {
                "adapter": "XMLAdapter", 
                "standards": ["MAVLink", "Generic Protocol", "Generic"],
                "features": [
                    "结构化数据提取",
                    "自动YAML转换",
                    "命名空间支持",
                    "验证和清洗"
                ],
                "examples": ["common.xml", "demo_protocol.xml"]
            },
            "JSON": {
                "adapter": "JSONAdapter",
                "standards": ["SIM", "Protocol Definition", "Generic"],
                "features": [
                    "直接格式转换",
                    "结构验证",
                    "嵌套对象处理",
                    "标准化包装"
                ],
                "examples": ["demo_protocol.json"]
            },
            "CSV": {
                "adapter": "CSVAdapter",
                "standards": ["Protocol Definition", "Enum Definition", "Generic"],
                "features": [
                    "智能列检测",
                    "类型推断",
                    "批量字段处理",
                    "关系重建"
                ],
                "examples": ["demo_fields.csv"]
            }
        },
        
        "demo_processing_scenarios": [
            {
                "scenario": "混合格式批量处理",
                "description": "同时处理PDF、XML、JSON、CSV多种格式的文件",
                "input_files": len(file_info["demo_files"]) + len(file_info["existing_test_files"]),
                "expected_output": "统一的YAML格式文件，可直接导入数据库",
                "processing_time": "预计 30-60 秒",
                "api_endpoint": "/api/universal/complete-pipeline"
            },
            {
                "scenario": "智能格式检测",
                "description": "自动识别文件格式和标准类型，选择最佳处理方案",
                "features": [
                    "MIME类型检测",
                    "内容分析",
                    "置信度评估",
                    "适配器匹配"
                ],
                "api_endpoint": "/api/universal/detect-format"
            },
            {
                "scenario": "目录批量处理",
                "description": "处理整个目录下的所有支持格式文件",
                "advantages": [
                    "无需手动选择文件",
                    "支持文件模式匹配",
                    "自动跳过不支持格式",
                    "统一输出管理"
                ],
                "api_endpoint": "/api/universal/process-directory"
            }
        ],
        
        "system_architecture": {
            "core_components": [
                "UniversalImportSystem (主控制器)",
                "FormatAdapter (格式适配器抽象)",
                "PDFAdapter (PDF处理)",
                "XMLAdapter (XML处理)",
                "JSONAdapter (JSON处理)",
                "CSVAdapter (CSV处理)"
            ],
            "processing_pipeline": [
                "1. 文件格式检测",
                "2. 标准类型识别",
                "3. 适配器选择",
                "4. 专用处理执行",
                "5. YAML标准化输出",
                "6. 数据库导入（可选）"
            ],
            "integration_points": [
                "现有PDF处理器 (pdf_adapter)",
                "MQTT处理器 (mqtt_adapter)", 
                "MAVLink转换器 (xml_to_pdf_converter)",
                "YAML导入器 (import_yaml)",
                "数据库连接 (db.py)"
            ]
        },
        
        "api_endpoints": {
            "核心接口": [
                "GET /api/universal/status - 系统状态",
                "GET /api/universal/supported-formats - 支持格式",
                "POST /api/universal/detect-format - 格式检测",
                "POST /api/universal/process-file - 单文件处理",
                "POST /api/universal/process-batch - 批量处理",
                "POST /api/universal/complete-pipeline - 完整流水线"
            ],
            "便捷接口": [
                "POST /api/universal/pdf/auto-process - 智能PDF处理",
                "POST /api/universal/xml/auto-process - 智能XML处理",
                "POST /api/universal/process-directory - 目录处理",
                "POST /api/universal/import-yaml - YAML导入"
            ],
            "管理接口": [
                "GET /api/universal/processing-history - 处理历史",
                "DELETE /api/universal/cleanup-temp - 清理临时文件",
                "GET /api/universal/health - 健康检查"
            ]
        },
        
        "usage_examples": {
            "单文件处理": {
                "curl_command": 'curl -X POST "http://localhost:8000/api/universal/process-file" -F "file=@demo_protocol.json"',
                "description": "上传并处理单个JSON文件"
            },
            "批量处理": {
                "curl_command": 'curl -X POST "http://localhost:8000/api/universal/process-batch" -F "files=@file1.pdf" -F "files=@file2.xml" -F "files=@file3.json"',
                "description": "同时处理多个不同格式的文件"
            },
            "完整流水线": {
                "curl_command": 'curl -X POST "http://localhost:8000/api/universal/complete-pipeline" -F "files=@demo.pdf" -F "import_to_db=true" -F "dry_run=false"',
                "description": "处理文件并直接导入数据库"
            },
            "目录处理": {
                "curl_command": 'curl -X POST "http://localhost:8000/api/universal/process-directory?directory_path=./test_sample&file_pattern=*.pdf"',
                "description": "处理目录下所有PDF文件"
            }
        },
        
        "advantages": [
            "🎯 自动格式识别 - 无需手动指定文件类型",
            "🔧 智能适配器选择 - 根据内容选择最佳处理方案",
            "📦 统一输出格式 - 所有格式转换为标准YAML",
            "🔄 现有系统集成 - 复用已有的专用处理器",
            "⚡ 批量处理支持 - 支持混合格式批量处理",
            "💾 数据库直连 - 可选的一站式导入服务",
            "🛡️ 错误容忍 - 单个文件失败不影响批量处理",
            "📊 详细报告 - 完整的处理统计和错误信息"
        ],
        
        "demo_files_created": {
            "directory": file_info["demo_directory"],
            "files": [
                {
                    "name": "demo_protocol.json",
                    "type": "JSON协议定义",
                    "size": "~1KB",
                    "content": "消息定义、字段结构、枚举类型"
                },
                {
                    "name": "demo_protocol.xml", 
                    "type": "XML协议定义",
                    "size": "~800B",
                    "content": "简化的协议结构、消息和枚举"
                },
                {
                    "name": "demo_fields.csv",
                    "type": "CSV字段定义",
                    "size": "~300B", 
                    "content": "字段名、位数、描述、类型、单位"
                }
            ]
        },
        
        "next_steps": [
            "1. 启动系统: uvicorn backend.main:app --reload",
            "2. 访问API文档: http://localhost:8000/docs",
            "3. 测试格式检测: POST /api/universal/detect-format",
            "4. 执行演示处理: POST /api/universal/process-batch",
            "5. 查看系统状态: GET /api/universal/status",
            "6. 清理演示文件: DELETE /api/universal/cleanup-temp"
        ]
    }
    
    # 保存报告
    report_path = "UNIVERSAL_IMPORT_SYSTEM_DEMO.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report, report_path

def main():
    """主演示函数"""
    print("🎯 统一多格式自动化导入系统演示")
    print("=" * 60)
    
    # 生成演示报告
    report, report_path = generate_processing_report()
    
    print("📊 系统能力概览:")
    print(f"   📄 支持格式: {len(report['supported_formats'])} 种")
    print(f"   🔧 适配器数量: {len(report['supported_formats'])} 个")
    print(f"   🌐 API接口: {len(report['api_endpoints']['核心接口']) + len(report['api_endpoints']['便捷接口'])} 个")
    print(f"   📋 处理场景: {len(report['demo_processing_scenarios'])} 种")
    
    print("\\n📁 演示文件已创建:")
    for file_info in report["demo_files_created"]["files"]:
        print(f"   📄 {file_info['name']} ({file_info['type']}) - {file_info['size']}")
    
    print("\\n🔧 支持的格式:")
    for format_name, format_info in report["supported_formats"].items():
        print(f"   📋 {format_name}: {', '.join(format_info['standards'])}")
    
    print("\\n🚀 核心优势:")
    for advantage in report["advantages"]:
        print(f"   {advantage}")
    
    print("\\n🔗 主要API接口:")
    for endpoint in report["api_endpoints"]["核心接口"][:5]:
        print(f"   🌐 {endpoint}")
    
    print(f"\\n📄 详细报告已保存: {report_path}")
    print(f"📁 演示文件目录: {report['demo_files_created']['directory']}")
    
    print("\\n🎉 统一多格式导入系统已就绪！")
    print("💡 现在您可以同时处理PDF、XML、JSON、CSV等多种格式的文件")

if __name__ == "__main__":
    main()

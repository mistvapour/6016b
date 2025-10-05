#!/usr/bin/env python3
"""
MAVLink XML到PDF转换器
将common.xml转换为可用于PDF处理流水线的格式化PDF文档
"""
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MAVLinkXMLConverter:
    """MAVLink XML到PDF数据转换器"""
    
    def __init__(self, xml_path="test_sample/common.xml"):
        self.xml_path = xml_path
        self.output_dir = "mavlink_output"
        self.data = {
            "enums": [],
            "messages": [],
            "commands": []
        }
    
    def parse_xml(self):
        """解析XML文件"""
        logger.info(f"📄 解析XML文件: {self.xml_path}")
        
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            logger.info(f"✅ XML文件解析成功")
            logger.info(f"   根元素: {root.tag}")
            logger.info(f"   版本: {root.find('version').text if root.find('version') is not None else '未知'}")
            logger.info(f"   方言: {root.find('dialect').text if root.find('dialect') is not None else '未知'}")
            
            return root
            
        except Exception as e:
            logger.error(f"❌ XML解析失败: {e}")
            raise
    
    def extract_enums(self, root):
        """提取枚举定义"""
        logger.info("🔄 提取枚举定义...")
        
        enums_element = root.find('enums')
        if enums_element is None:
            logger.warning("⚠️ 未找到enums元素")
            return
        
        enum_count = 0
        for enum in enums_element.findall('enum'):
            enum_data = {
                "name": enum.get('name', ''),
                "description": "",
                "bitmask": enum.get('bitmask', 'false') == 'true',
                "entries": []
            }
            
            # 获取描述
            desc_elem = enum.find('description')
            if desc_elem is not None:
                enum_data["description"] = desc_elem.text or ""
            
            # 获取条目
            for entry in enum.findall('entry'):
                entry_data = {
                    "value": entry.get('value', ''),
                    "name": entry.get('name', ''),
                    "description": ""
                }
                
                entry_desc = entry.find('description')
                if entry_desc is not None:
                    entry_data["description"] = entry_desc.text or ""
                
                enum_data["entries"].append(entry_data)
            
            self.data["enums"].append(enum_data)
            enum_count += 1
        
        logger.info(f"✅ 提取了 {enum_count} 个枚举定义")
    
    def extract_messages(self, root):
        """提取消息定义"""
        logger.info("🔄 提取消息定义...")
        
        messages_element = root.find('messages')
        if messages_element is None:
            logger.warning("⚠️ 未找到messages元素")
            return
        
        message_count = 0
        for message in messages_element.findall('message'):
            message_data = {
                "id": message.get('id', ''),
                "name": message.get('name', ''),
                "description": "",
                "fields": []
            }
            
            # 获取描述
            desc_elem = message.find('description')
            if desc_elem is not None:
                message_data["description"] = desc_elem.text or ""
            
            # 获取字段
            for field in message.findall('field'):
                field_data = {
                    "type": field.get('type', ''),
                    "name": field.get('name', ''),
                    "units": field.get('units', ''),
                    "description": field.text or "",
                    "enum": field.get('enum', ''),
                    "display": field.get('display', ''),
                    "print_format": field.get('print_format', '')
                }
                
                message_data["fields"].append(field_data)
            
            self.data["messages"].append(message_data)
            message_count += 1
        
        logger.info(f"✅ 提取了 {message_count} 个消息定义")
    
    def generate_pdf_content(self):
        """生成适合PDF转换的内容"""
        logger.info("📄 生成PDF内容...")
        
        # 创建输出目录
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # 生成HTML内容（用于PDF转换）
        html_content = self.create_html_document()
        
        # 保存HTML文件
        html_path = Path(self.output_dir) / "mavlink_protocol.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML文档已生成: {html_path}")
        
        # 生成JSON数据文件
        json_path = Path(self.output_dir) / "mavlink_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON数据已生成: {json_path}")
        
        return html_path, json_path
    
    def create_html_document(self):
        """创建HTML文档"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAVLink Protocol Documentation</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        h3 {{
            color: #2980b9;
            margin-top: 25px;
        }}
        .enum-section, .message-section {{
            margin-bottom: 30px;
            border: 1px solid #ecf0f1;
            padding: 20px;
            border-radius: 5px;
        }}
        .enum-entry, .field-entry {{
            background-color: #f8f9fa;
            margin: 10px 0;
            padding: 10px;
            border-left: 4px solid #3498db;
        }}
        .value {{
            font-weight: bold;
            color: #e74c3c;
        }}
        .name {{
            font-weight: bold;
            color: #27ae60;
        }}
        .description {{
            color: #7f8c8d;
            font-style: italic;
            margin-top: 5px;
        }}
        .field-type {{
            background-color: #3498db;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .units {{
            background-color: #f39c12;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .toc {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 5px 0;
        }}
        .toc a {{
            color: #2980b9;
            text-decoration: none;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>MAVLink Protocol Documentation</h1>
    <p><strong>生成时间:</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    <p><strong>源文件:</strong> {self.xml_path}</p>
    <p><strong>协议版本:</strong> MAVLink Common Messages</p>
    
    <div class="toc">
        <h2>目录</h2>
        <ul>
            <li><a href="#enums">1. 枚举定义 ({len(self.data['enums'])} 个)</a></li>
            <li><a href="#messages">2. 消息定义 ({len(self.data['messages'])} 个)</a></li>
            <li><a href="#summary">3. 统计摘要</a></li>
        </ul>
    </div>
"""
        
        # 添加枚举部分
        if self.data["enums"]:
            html += self.generate_enums_html()
        
        # 添加消息部分
        if self.data["messages"]:
            html += self.generate_messages_html()
        
        # 添加统计摘要
        html += self.generate_summary_html()
        
        html += """
</body>
</html>"""
        
        return html
    
    def generate_enums_html(self):
        """生成枚举HTML"""
        html = """
    <h2 id="enums">1. 枚举定义</h2>
    <p>以下是MAVLink协议中定义的所有枚举类型：</p>
"""
        
        for i, enum in enumerate(self.data["enums"][:10], 1):  # 只显示前10个避免过长
            bitmask_text = " (位掩码)" if enum["bitmask"] else ""
            html += f"""
    <div class="enum-section">
        <h3>{i}. {enum['name']}{bitmask_text}</h3>
        <div class="description">{enum['description']}</div>
        
        <table>
            <tr>
                <th>值</th>
                <th>名称</th>
                <th>描述</th>
            </tr>
"""
            
            for entry in enum["entries"][:15]:  # 每个枚举只显示前15个条目
                html += f"""
            <tr>
                <td class="value">{entry['value']}</td>
                <td class="name">{entry['name']}</td>
                <td>{entry['description']}</td>
            </tr>
"""
            
            html += """
        </table>
    </div>
"""
        
        if len(self.data["enums"]) > 10:
            html += f"<p><em>... 还有 {len(self.data['enums']) - 10} 个枚举定义未显示</em></p>"
        
        return html
    
    def generate_messages_html(self):
        """生成消息HTML"""
        html = """
    <h2 id="messages">2. 消息定义</h2>
    <p>以下是MAVLink协议中定义的消息格式：</p>
"""
        
        for i, message in enumerate(self.data["messages"][:15], 1):  # 只显示前15个消息
            html += f"""
    <div class="message-section">
        <h3>{i}. {message['name']} (ID: {message['id']})</h3>
        <div class="description">{message['description']}</div>
        
        <table>
            <tr>
                <th>字段名</th>
                <th>类型</th>
                <th>单位</th>
                <th>描述</th>
            </tr>
"""
            
            for field in message["fields"]:
                units_tag = f'<span class="units">{field["units"]}</span>' if field["units"] else ""
                html += f"""
            <tr>
                <td class="name">{field['name']}</td>
                <td><span class="field-type">{field['type']}</span></td>
                <td>{units_tag}</td>
                <td>{field['description']}</td>
            </tr>
"""
            
            html += """
        </table>
    </div>
"""
        
        if len(self.data["messages"]) > 15:
            html += f"<p><em>... 还有 {len(self.data['messages']) - 15} 个消息定义未显示</em></p>"
        
        return html
    
    def generate_summary_html(self):
        """生成统计摘要HTML"""
        total_enum_entries = sum(len(enum["entries"]) for enum in self.data["enums"])
        total_message_fields = sum(len(msg["fields"]) for msg in self.data["messages"])
        
        html = f"""
    <h2 id="summary">3. 统计摘要</h2>
    <div class="enum-section">
        <h3>协议统计信息</h3>
        <table>
            <tr>
                <th>项目</th>
                <th>数量</th>
                <th>说明</th>
            </tr>
            <tr>
                <td>枚举类型</td>
                <td class="value">{len(self.data["enums"])}</td>
                <td>协议中定义的枚举类型总数</td>
            </tr>
            <tr>
                <td>枚举条目</td>
                <td class="value">{total_enum_entries}</td>
                <td>所有枚举类型中的条目总数</td>
            </tr>
            <tr>
                <td>消息类型</td>
                <td class="value">{len(self.data["messages"])}</td>
                <td>协议中定义的消息类型总数</td>
            </tr>
            <tr>
                <td>消息字段</td>
                <td class="value">{total_message_fields}</td>
                <td>所有消息中的字段总数</td>
            </tr>
        </table>
        
        <h3>转换信息</h3>
        <ul>
            <li><strong>源文件:</strong> {self.xml_path}</li>
            <li><strong>转换时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            <li><strong>协议类型:</strong> MAVLink Common Messages</li>
            <li><strong>输出格式:</strong> HTML (可转换为PDF)</li>
        </ul>
    </div>
"""
        
        return html
    
    def convert_to_pdf_using_weasyprint(self, html_path):
        """使用WeasyPrint将HTML转换为PDF"""
        try:
            from weasyprint import HTML, CSS
            
            pdf_path = Path(self.output_dir) / "mavlink_protocol.pdf"
            
            # 创建CSS样式
            css = CSS(string="""
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-size: 12pt;
                }
                h1 {
                    page-break-before: always;
                }
                .enum-section, .message-section {
                    page-break-inside: avoid;
                }
            """)
            
            # 转换为PDF
            HTML(filename=str(html_path)).write_pdf(str(pdf_path), stylesheets=[css])
            
            logger.info(f"✅ PDF文件已生成: {pdf_path}")
            return pdf_path
            
        except ImportError:
            logger.warning("⚠️ WeasyPrint未安装，无法直接转换为PDF")
            logger.info("💡 请安装: pip install weasyprint")
            return None
        except Exception as e:
            logger.error(f"❌ PDF转换失败: {e}")
            return None
    
    def create_yaml_mapping(self):
        """创建适合现有系统的YAML映射"""
        logger.info("📄 创建YAML映射...")
        
        yaml_content = f"""# MAVLink协议YAML映射
# 生成时间: {datetime.now().isoformat()}
# 源文件: {self.xml_path}

standard: MAVLink
edition: "Common"
transport_unit: byte

# 枚举定义映射到现有系统
enums:
"""
        
        # 添加部分枚举示例
        for enum in self.data["enums"][:5]:
            yaml_content += f"""- key: {enum['name'].lower()}
  description: "{enum['description'][:100]}..."
  items:
"""
            for entry in enum["entries"][:10]:
                yaml_content += f"""  - code: "{entry['value']}"
    label: "{entry['name']}"
    description: "{entry['description'][:50]}..."
"""
        
        yaml_content += """
# 消息定义映射
spec_messages:
"""
        
        # 添加部分消息示例
        for message in self.data["messages"][:3]:
            yaml_content += f"""- label: {message['name']}
  title: "{message['name']} Message"
  message_id: {message['id']}
  description: "{message['description'][:100]}..."
  segments:
  - type: "Data Fields"
    seg_idx: 0
    fields:
"""
            for field in message["fields"][:5]:
                yaml_content += f"""    - name: "{field['name']}"
      type: "{field['type']}"
      units: "{field['units']}"
      description: "{field['description'][:50]}..."
"""
        
        yaml_content += f"""
# 元数据
metadata:
  source_file: "{self.xml_path}"
  total_enums: {len(self.data["enums"])}
  total_messages: {len(self.data["messages"])}
  conversion_date: "{datetime.now().isoformat()}"
  processor: "mavlink_xml_converter"
"""
        
        # 保存YAML文件
        yaml_path = Path(self.output_dir) / "mavlink_mapping.yaml"
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        logger.info(f"✅ YAML映射已生成: {yaml_path}")
        return yaml_path
    
    def run_conversion(self):
        """运行完整转换流程"""
        logger.info("🚀 开始MAVLink XML到PDF转换")
        logger.info("=" * 60)
        
        try:
            # 1. 解析XML
            root = self.parse_xml()
            
            # 2. 提取数据
            self.extract_enums(root)
            self.extract_messages(root)
            
            # 3. 生成HTML和JSON
            html_path, json_path = self.generate_pdf_content()
            
            # 4. 尝试转换为PDF
            pdf_path = self.convert_to_pdf_using_weasyprint(html_path)
            
            # 5. 创建YAML映射
            yaml_path = self.create_yaml_mapping()
            
            # 结果汇总
            result = {
                "success": True,
                "files_generated": {
                    "html": str(html_path),
                    "json": str(json_path),
                    "yaml": str(yaml_path),
                    "pdf": str(pdf_path) if pdf_path else None
                },
                "statistics": {
                    "enums": len(self.data["enums"]),
                    "messages": len(self.data["messages"]),
                    "total_enum_entries": sum(len(e["entries"]) for e in self.data["enums"]),
                    "total_message_fields": sum(len(m["fields"]) for m in self.data["messages"])
                }
            }
            
            logger.info("🎉 转换完成！")
            logger.info("=" * 60)
            logger.info("📊 转换统计:")
            logger.info(f"   📋 枚举类型: {result['statistics']['enums']}")
            logger.info(f"   📧 消息类型: {result['statistics']['messages']}")
            logger.info(f"   🔧 枚举条目: {result['statistics']['total_enum_entries']}")
            logger.info(f"   📄 消息字段: {result['statistics']['total_message_fields']}")
            logger.info("📁 生成文件:")
            for file_type, path in result["files_generated"].items():
                if path:
                    logger.info(f"   {file_type.upper()}: {path}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 转换失败: {e}")
            return {"success": False, "error": str(e)}

def main():
    """主函数"""
    converter = MAVLinkXMLConverter()
    result = converter.run_conversion()
    
    if result["success"]:
        print("\\n🎯 后续步骤:")
        print("1. 查看生成的HTML文件预览内容")
        print("2. 如果需要PDF，安装weasyprint: pip install weasyprint")
        print("3. 使用现有PDF处理流水线处理生成的PDF")
        print("4. 或直接使用生成的YAML文件导入数据库")
        
        html_path = result["files_generated"]["html"]
        yaml_path = result["files_generated"]["yaml"]
        
        print("\\n🔧 推荐命令:")
        print(f"# 在浏览器中查看HTML:")
        print(f"open {html_path}")
        print(f"\\n# 直接导入YAML到数据库:")
        print(f'curl -X POST "http://localhost:8000/api/import/yaml" \\\\')
        print(f'     -d \'{{"yaml_path": "{yaml_path}", "dry_run": true}}\'')
    else:
        print(f"❌ 转换失败: {result.get('error')}")

if __name__ == "__main__":
    main()

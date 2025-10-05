# MQTT PDF处理流水线使用指南

## 🎯 概述

本文档介绍如何使用新实现的MQTT PDF处理流水线，该流水线专门针对OASIS MQTT v5.0标准文档，实现从PDF文档到数据库的全自动化处理。

## 🚀 快速开始

### 1. 前提条件

确保已安装以下依赖：

```bash
# Python依赖
pip install camelot-py[cv] pdfplumber PyMuPDF pyyaml fastapi uvicorn pandas requests

# 系统依赖
# Windows: 安装Ghostscript
# Linux: apt-get install libgl1-mesa-glx
```

### 2. 启动服务

```bash
# 启动后端API服务
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 验证服务状态
curl http://localhost:8000/api/health
curl http://localhost:8000/api/mqtt/health
```

### 3. 一键测试

```bash
# 运行快速测试脚本
python quick_test_mqtt.py

# 或运行完整测试
python test_mqtt_pipeline.py
```

## 📋 API接口说明

### 1. PDF到YAML转换

**接口**: `POST /api/mqtt/pdf_to_yaml`

**参数**:
- `file`: PDF文件（multipart/form-data）
- `pages`: 页面范围，例如 "10-130" 或 "10-20,25-30"
- `output_dir`: 输出目录（可选，默认"mqtt_output"）

**示例**:
```bash
curl -X POST "http://localhost:8000/api/mqtt/pdf_to_yaml?pages=10-50&output_dir=my_output" \
     -F "file=@mqtt-v5.0.pdf"
```

**响应**:
```json
{
  "success": true,
  "message": "Successfully processed MQTT PDF with 2 control packets",
  "data": {
    "pdf_filename": "mqtt-v5.0.pdf",
    "pages_processed": 41,
    "sections_found": 2,
    "tables_extracted": 4,
    "messages_created": 2,
    "total_fields": 15,
    "output_dir": "my_output",
    "files": ["..."],
    "main_yaml": "my_output/mqtt_v5_complete.yaml",
    "main_json": "my_output/mqtt_v5_complete.json"
  }
}
```

### 2. 完整流水线

**接口**: `POST /api/mqtt/complete_pipeline`

**参数**:
- `file`: PDF文件
- `pages`: 页面范围
- `output_dir`: 输出目录
- `import_to_db`: 是否导入数据库（默认false）
- `dry_run`: 数据库导入是否试运行（默认true）

**示例**:
```bash
curl -X POST "http://localhost:8000/api/mqtt/complete_pipeline?pages=10-50&import_to_db=true&dry_run=true" \
     -F "file=@mqtt-v5.0.pdf"
```

### 3. YAML验证

**接口**: `POST /api/mqtt/validate_yaml`

**示例**:
```bash
curl -X POST "http://localhost:8000/api/mqtt/validate_yaml?yaml_path=mqtt_output/mqtt_v5_complete.yaml"
```

### 4. 数据库导入

**接口**: `POST /api/import/yaml`

**示例**:
```bash
# 试运行
curl -X POST "http://localhost:8000/api/import/yaml?yaml_path=mqtt_output/mqtt_v5_complete.yaml&dry_run=true"

# 实际导入
curl -X POST "http://localhost:8000/api/import/yaml?yaml_path=mqtt_output/mqtt_v5_complete.yaml&dry_run=false"
```

## 🔧 核心功能

### 1. 智能表格提取

- **双路抽取**: 同时使用Camelot和pdfplumber提取表格
- **智能评分**: 基于表头关键词和结构特征选择最佳表格
- **MQTT特化**: 针对MQTT文档的表格结构优化识别算法

### 2. 章节识别

- **控制报文识别**: 自动识别CONNECT、PUBLISH、SUBSCRIBE等报文章节
- **子章节解析**: 识别Fixed Header、Variable Header、Properties、Payload等子结构
- **页面关联**: 将表格数据与相应章节关联

### 3. 字段标准化

- **编码识别**: 自动识别VBI、UTF8、UINT、BIN等编码类型
- **长度解析**: 解析"2 bytes"、"VBI"、"UTF-8 string"等长度描述
- **偏移计算**: 自动计算字段在报文中的偏移量

### 4. SIM构建

**中间语义模型结构**:
```yaml
standard: OASIS MQTT
edition: '5.0'
transport_unit: byte
enums: [...]
spec_messages:
  - label: CONNECT
    segments:
      - type: Fixed Header
        fields: [...]
      - type: Variable Header  
        fields: [...]
```

### 5. 多格式导出

- **主YAML**: 完整的SIM数据
- **JSON格式**: 便于程序处理
- **单独消息**: 每个控制报文单独的YAML文件
- **枚举定义**: 独立的枚举配置文件
- **导入清单**: 文件清单和元数据

## 📁 输出文件结构

```
mqtt_output/
├── mqtt_v5_complete.yaml      # 主YAML文件
├── mqtt_v5_complete.json       # JSON格式
├── mqtt_enums.yaml            # 枚举定义
├── import_manifest.yaml       # 导入清单
└── messages/                  # 单独消息文件
    ├── connect_message.yaml
    ├── publish_message.yaml
    └── subscribe_message.yaml
```

## 🔍 质量校验

### 1. 结构校验

- **必填字段**: 检查label、title、segments等必需字段
- **数据类型**: 验证字段类型和格式
- **一致性**: 检查编码类型与长度的一致性

### 2. 逻辑校验

- **字段完整性**: 检查UINT类型字段是否有固定长度
- **变长字段**: 验证VBI、UTF8等变长字段的定义
- **重复检查**: 检测段内重复字段定义

### 3. MQTT特定校验

- **报文类型**: 验证MQTT控制报文的完整性
- **属性映射**: 检查Properties段的属性ID合法性
- **QoS级别**: 验证QoS相关枚举的正确性

## ⚡ 性能优化

### 1. 页面范围优化

```bash
# 推荐：指定具体页面范围
pages=10-50

# 避免：处理整个文档
pages=1-200
```

### 2. 并发处理

- 表格提取支持并发处理
- 支持多个PDF文件批量处理
- 内存使用优化，避免OOM

### 3. 缓存机制

- 表格提取结果缓存
- 章节识别结果缓存
- 重复处理检测

## 🐛 故障排除

### 1. 常见问题

**问题**: 无法识别MQTT章节
```bash
# 检查页面范围是否包含控制报文标题
# 确保PDF文本可提取（非纯图片扫描）
```

**问题**: 表格提取失败
```bash
# 尝试不同的页面范围
# 检查PDF表格是否为标准格式
# 查看日志了解具体错误
```

**问题**: 字段解析错误
```bash
# 检查表格列头是否标准
# 确认字段描述格式正确
# 查看validation_result了解详情
```

### 2. 调试技巧

```bash
# 查看详细日志
tail -f logs/pdf_processing.log

# 验证中间结果
curl -X POST "http://localhost:8000/api/mqtt/validate_yaml?yaml_path=output.yaml"

# 检查文件列表
curl "http://localhost:8000/api/mqtt/list_outputs?output_dir=mqtt_output"
```

### 3. 日志分析

```bash
# 搜索错误信息
grep "ERROR" logs/app.log

# 查看MQTT处理日志
grep "mqtt" logs/pdf_processing.log

# 分析性能信息
grep "Processing time" logs/app.log
```

## 🔄 集成示例

### 1. Python集成

```python
import requests

# PDF处理
with open('mqtt-v5.0.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/mqtt/complete_pipeline',
        files={'file': f},
        params={
            'pages': '10-50',
            'import_to_db': True,
            'dry_run': False
        }
    )

result = response.json()
if result['success']:
    print(f"处理成功: {result['message']}")
```

### 2. 批量处理

```bash
#!/bin/bash
# 批量处理多个MQTT PDF文件

for pdf in *.pdf; do
    echo "Processing $pdf..."
    curl -X POST "http://localhost:8000/api/mqtt/complete_pipeline" \
         -F "file=@$pdf" \
         -F "pages=10-100" \
         -F "import_to_db=true" \
         -F "dry_run=false"
done
```

### 3. 自动化脚本

```python
# 监控目录，自动处理新的PDF文件
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.pdf'):
            process_mqtt_pdf(event.src_path)

def process_mqtt_pdf(pdf_path):
    # 调用MQTT处理API
    pass

# 启动监控
observer = Observer()
observer.schedule(PDFHandler(), path='./input', recursive=False)
observer.start()
```

## 📈 扩展开发

### 1. 添加新的标准支持

```python
# 在mqtt_adapter/parse_sections.py中添加新的正则模式
NEW_PROTOCOL_RE = re.compile(r'^(COMMAND|RESPONSE|EVENT)\b', re.I)

# 在normalize_bits.py中添加新的编码类型
NEW_ENCODING = "CUSTOM"
```

### 2. 自定义字段解析

```python
# 扩展parse_field_row函数
def parse_custom_field(row_data):
    # 自定义解析逻辑
    pass
```

### 3. 新增校验规则

```python
# 在build_sim.py中添加自定义校验
def validate_custom_rule(sim):
    # 自定义校验逻辑
    pass
```

## 📞 技术支持

### 1. 联系方式

- **文档**: 查看本指南和API文档
- **日志**: 检查系统日志获取详细信息
- **测试**: 使用提供的测试脚本验证功能

### 2. 贡献指南

- 报告Bug: 提供完整的错误日志和复现步骤
- 功能建议: 描述使用场景和预期效果
- 代码贡献: 遵循项目编码规范

### 3. 版本更新

- 定期更新依赖包版本
- 关注MQTT标准更新
- 及时更新文档和示例

---

**注意**: 本流水线专门针对MQTT v5.0标准优化，对于其他协议标准可能需要调整识别规则和解析逻辑。

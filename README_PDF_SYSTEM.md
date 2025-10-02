# PDF标准文档处理系统

## 项目概述

本项目实现了一个完整的PDF标准文档到数据库的批量处理流水线，专门针对MIL-STD-6016等军事标准文档。系统采用"适配器 + 模板识别 + 中间语义模型（SIM） + 校验 + 映射 YAML + 导入器"的六步流水线架构，实现了"可批量、可追溯、可回滚"的文档处理需求。

## 系统特性

### 🚀 核心功能
- **智能PDF解析**：支持文本型和扫描型PDF，自动选择最佳提取方法
- **章节模板识别**：专门针对MIL-STD-6016的J系列和Appendix B章节定位
- **双路表格提取**：Camelot + pdfplumber，置信度自动选择最佳结果
- **数据标准化**：位段格式统一、单位转换、字段清洗
- **中间语义模型**：结构化的SIM模型，便于后续处理
- **全面数据校验**：位段、词典树、单位、版本一致性检查
- **半自动标注器**：可视化字段标注，提高数据质量

### 🏗️ 技术架构
- **后端**：FastAPI + Python，模块化设计
- **前端**：React + TypeScript + Tailwind CSS
- **数据库**：MySQL，支持现有数据模型
- **PDF处理**：PyMuPDF + pdfplumber + Camelot + Tesseract OCR

## 快速开始

### 1. 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd 6016-app

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 3. 配置数据库

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE milstd6016;
```

### 4. 启动系统

```bash
# 使用启动脚本（推荐）
python start_system.py

# 或手动启动
# 后端
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run dev
```

### 5. 访问系统

- 前端界面：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 使用流程

### 1. PDF处理
1. 打开前端界面，切换到"PDF处理"标签页
2. 上传PDF文件（支持MIL-STD-6016标准文档）
3. 选择标准类型和版本
4. 点击"开始处理"

### 2. 半自动标注
1. 在"字段标注"标签页查看提取的字段
2. 为每个字段选择对应的DFI/DUI/DI
3. 完成标注后导出结果

### 3. 结果导出
1. 查看处理结果和校验报告
2. 下载生成的YAML文件
3. 使用现有导入器导入数据库

## 项目结构

```
6016-app/
├── backend/                    # 后端服务
│   ├── pdf_adapter/           # PDF处理模块
│   │   ├── extract_tables.py  # 表格提取
│   │   ├── parse_sections.py  # 章节解析
│   │   ├── normalize_bits.py  # 数据标准化
│   │   ├── build_sim.py       # SIM构建
│   │   ├── validators.py      # 数据校验
│   │   └── pdf_processor.py   # 主处理器
│   ├── pdf_api.py             # PDF处理API
│   ├── main.py                # 主应用
│   └── requirements.txt       # Python依赖
├── frontend/                   # 前端界面
│   ├── src/
│   │   ├── components/
│   │   │   └── PDFProcessor.tsx # PDF处理组件
│   │   └── App.tsx            # 主应用
│   └── package.json           # Node.js依赖
├── start_system.py            # 系统启动脚本
├── test_pdf_processing.py     # 测试脚本
└── PDF_PROCESSING_GUIDE.md    # 详细使用指南
```

## API接口

### PDF处理
```http
POST /api/pdf/process
Content-Type: multipart/form-data

file: PDF文件
standard: 标准名称
edition: 版本
```

### 批量处理
```http
POST /api/pdf/batch-process
Content-Type: application/json

{
  "pdf_dir": "PDF文件目录",
  "output_dir": "输出目录",
  "standard": "MIL-STD-6016",
  "edition": "B"
}
```

### 数据验证
```http
POST /api/pdf/validate
Content-Type: application/json

{
  "sim_data": { /* SIM数据 */ }
}
```

## 核心算法

### 1. 表格提取算法
- **双路抽取**：Camelot lattice/stream + pdfplumber
- **置信度评分**：基于列头匹配、列数一致性、位段可解析性
- **自动选择**：选择置信度最高的提取结果

### 2. 章节识别算法
- **J系列识别**：正则匹配`^J\d+(\.\d+)?`模式
- **Appendix B定位**：DFI/DUI/DI层级结构解析
- **表格关联**：基于页面位置和内容相似度

### 3. 数据标准化算法
- **位段归一**：统一各种位段格式（0-5, 0–5, 0..5等）
- **单位转换**：支持deg/rad, ft/m, kts/m/s等常用单位
- **字段清洗**：全角半角转换、连字替换、空格规范化

### 4. 校验算法
- **位段校验**：检查边界、重叠、覆盖率
- **词典树校验**：验证DFI/DUI/DI层级关系
- **单位校验**：检查单位定义和一致性

## 配置说明

### 后端配置
```python
# 数据库配置
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "password"
DB_NAME = "milstd6016"

# PDF处理配置
MAX_BITS = 70
MIN_CONFIDENCE = 0.7
```

### 前端配置
```typescript
// API地址配置
VITE_API_BASE_URL = "http://localhost:8000"

// 文件上传配置
MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
```

## 测试

### 运行测试
```bash
# 测试PDF处理功能
cd backend
python test_pdf_processing.py

# 测试API接口
curl -X POST "http://localhost:8000/api/pdf/process" \
  -F "file=@test.pdf" \
  -F "standard=MIL-STD-6016" \
  -F "edition=B"
```

### 测试数据
- 使用MIL-STD-6016标准PDF文档
- 确保PDF包含J系列消息和Appendix B
- 验证提取结果的准确性

## 性能优化

### 1. 大文件处理
- 分页处理大型PDF
- 异步处理长时间任务
- 进度显示和取消功能

### 2. 批量处理
- 并行处理多个PDF
- 队列管理
- 错误恢复机制

### 3. 缓存优化
- 提取结果缓存
- 候选数据缓存
- 校验结果缓存

## 故障排除

### 常见问题

1. **PDF提取失败**
   - 检查PDF是否为扫描件
   - 确认PDF文件完整
   - 尝试调整Camelot参数

2. **位段解析错误**
   - 检查表格格式
   - 确认位段列格式
   - 手动调整位段格式

3. **标注候选为空**
   - 检查数据库数据
   - 确认字段名匹配
   - 手动添加候选数据

4. **校验错误**
   - 检查位段重叠
   - 确认单位定义
   - 验证层级关系

### 日志查看
```bash
# 后端日志
tail -f backend/logs/app.log

# 前端日志
# 在浏览器开发者工具中查看
```

## 扩展开发

### 添加新标准支持
1. 在`parse_sections.py`中添加新的章节识别模式
2. 在`normalize_bits.py`中添加新的位段格式
3. 在`build_sim.py`中调整SIM结构

### 自定义校验规则
1. 在`validators.py`中添加新的校验器
2. 在`ComprehensiveValidator`中集成新校验器
3. 更新前端显示新的校验结果

### 改进标注器
1. 在`PDFProcessor.tsx`中添加新的标注功能
2. 实现更智能的候选推荐算法
3. 添加批量标注操作

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请联系开发团队或查看项目文档。

---

**注意**：本系统专门针对MIL-STD-6016标准文档设计，如需支持其他标准，请参考扩展开发部分。

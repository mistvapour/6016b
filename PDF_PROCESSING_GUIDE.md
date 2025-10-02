# PDF标准文档处理系统使用指南

## 系统概述

本系统实现了完整的PDF标准文档到数据库的批量处理流水线，支持"可批量、可追溯、可回滚"的文档处理需求。系统采用"适配器 + 模板识别 + 中间语义模型（SIM） + 校验 + 映射 YAML + 导入器"的六步流水线架构。

## 系统架构

### 后端组件

1. **PDF适配器层** (`backend/pdf_adapter/`)
   - `extract_tables.py`: 表格提取，支持Camelot和pdfplumber双路抽取
   - `parse_sections.py`: 章节解析，专门针对MIL-STD-6016的J系列和Appendix B
   - `normalize_bits.py`: 位段和单位标准化
   - `build_sim.py`: 中间语义模型构建
   - `validators.py`: 数据校验与质检
   - `pdf_processor.py`: 主处理器，整合所有功能

2. **API接口** (`backend/pdf_api.py`)
   - PDF上传和处理接口
   - 批量处理接口
   - 数据验证接口
   - 文件下载接口

### 前端组件

1. **PDF处理界面** (`frontend/src/components/PDFProcessor.tsx`)
   - 文件上传和参数配置
   - 处理结果展示
   - 半自动标注器
   - 校验报告查看

## 使用流程

### 1. 环境准备

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install

# 启动后端服务
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端服务
cd frontend
npm run dev
```

### 2. PDF处理流程

#### 步骤1: 上传PDF文件
1. 打开前端界面，切换到"PDF处理"标签页
2. 选择PDF文件（支持MIL-STD-6016标准文档）
3. 选择标准类型（默认MIL-STD-6016）
4. 选择版本（A/B/C）
5. 点击"开始处理"

#### 步骤2: 自动处理
系统会自动执行以下步骤：
1. **PDF适配器层**：区分文本型和扫描型PDF，使用相应提取方法
2. **章节识别**：定位J系列消息和Appendix B章节
3. **表格提取**：使用Camelot和pdfplumber双路抽取表格数据
4. **数据标准化**：统一位段格式、单位、字段名等
5. **SIM构建**：生成中间语义模型
6. **数据校验**：检查位段重叠、覆盖率、单位一致性等

#### 步骤3: 半自动标注
1. 在"字段标注"标签页查看提取的字段
2. 为每个字段选择对应的DFI/DUI/DI
3. 系统提供候选数据项供选择
4. 完成标注后导出标注结果

#### 步骤4: 结果导出
1. 查看处理结果统计
2. 检查校验报告
3. 下载生成的YAML文件
4. 使用现有导入器导入数据库

## 核心功能

### 1. 智能表格提取
- **双路抽取**：Camelot lattice/stream + pdfplumber
- **置信度评分**：基于列头匹配、列数一致性、位段可解析性
- **自动选择**：选择置信度最高的提取结果

### 2. 章节模板识别
- **J系列识别**：正则匹配`^J\d+(\.\d+)?`模式
- **Appendix B定位**：DFI/DUI/DI层级结构解析
- **表格关联**：自动关联章节与相关表格

### 3. 数据标准化
- **位段归一**：统一各种位段格式（0-5, 0–5, 0..5等）
- **单位转换**：支持deg/rad, ft/m, kts/m/s等常用单位
- **字段清洗**：全角半角转换、连字替换、空格规范化

### 4. 中间语义模型(SIM)
```json
{
  "standard": "MIL-STD-6016",
  "edition": "B",
  "j_messages": [
    {
      "label": "J10.2",
      "title": "Weapon Status",
      "words": [
        {
          "type": "Initial",
          "word_idx": 0,
          "bitlen": 70,
          "fields": [
            {
              "name": "Weapon Status",
              "bits": [0, 5],
              "map": {
                "nullable": false,
                "description": "Current weapon status",
                "units": ["enum"]
              }
            }
          ]
        }
      ]
    }
  ],
  "dfi_dui_di": [...],
  "enums": [...],
  "units": [...]
}
```

### 5. 数据校验
- **位段校验**：检查边界、重叠、覆盖率
- **词典树校验**：验证DFI/DUI/DI层级关系
- **单位校验**：检查单位定义和一致性
- **版本校验**：检测版本间变化

### 6. 半自动标注器
- **候选推荐**：基于字段名相似度推荐DFI/DUI/DI
- **可视化标注**：位段条带显示，直观选择
- **批量导出**：支持标注结果批量导出

## API接口

### 1. PDF处理
```http
POST /api/pdf/process
Content-Type: multipart/form-data

file: PDF文件
standard: 标准名称
edition: 版本
```

### 2. 批量处理
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

### 3. 数据验证
```http
POST /api/pdf/validate
Content-Type: application/json

{
  "sim_data": {
    // SIM数据
  }
}
```

## 配置说明

### 后端配置
- 数据库连接：通过环境变量配置
- PDF处理参数：可在代码中调整
- 输出目录：支持自定义

### 前端配置
- API地址：通过环境变量`VITE_API_BASE_URL`配置
- 文件上传限制：默认10MB
- 显示选项：可配置显示字段

## 常见问题

### 1. PDF提取失败
- 检查PDF是否为扫描件，需要OCR处理
- 确认PDF文件完整，没有损坏
- 尝试调整Camelot参数

### 2. 位段解析错误
- 检查表格格式是否符合标准
- 确认位段列包含正确的范围格式
- 手动调整位段格式

### 3. 标注候选为空
- 检查数据库是否包含相关DFI/DUI/DI数据
- 确认字段名匹配规则
- 手动添加候选数据

### 4. 校验错误
- 检查位段是否重叠
- 确认单位定义正确
- 验证DFI/DUI/DI层级关系

## 扩展开发

### 添加新的标准支持
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

## 维护说明

### 1. 日志监控
- 处理过程日志
- 错误日志记录
- 性能指标监控

### 2. 数据备份
- 处理结果备份
- 标注数据备份
- 配置文件备份

### 3. 版本更新
- 依赖包更新
- 功能增强
- 兼容性维护

## 联系支持

如有问题或建议，请联系开发团队或查看项目文档。

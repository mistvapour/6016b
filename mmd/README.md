# 6016-app 系统架构 Mermaid 图表

本文件夹包含了 6016-app 系统的完整架构图表，使用 Mermaid 语法编写。

## 📊 图表列表

### 1. 系统概览图 (`system_overview.mmd`)
展示了整个系统的核心功能模块和主要数据流：
- 用户界面层
- 核心功能模块（PDF处理、MQTT处理、统一导入、CDM系统、语义互操作）
- 数据处理流水线
- 数据存储层
- 部署和监控

### 2. 核心价值主张图 (`core_value_proposition.mmd`)
展示了系统解决的核心业务问题和带来的价值：
- 业务挑战：大量PDF文档、多格式数据、数据质量、系统集成
- 解决方案：智能PDF处理、统一数据模型、全面数据验证、多协议支持
- 核心价值：效率提升、数据一致性、质量保证、系统互操作
- 技术优势：模块化架构、智能识别、容错设计、生产就绪
- 业务成果：处理速度提升、数据准确率、维护成本降低、系统集成简化

### 3. 系统总体架构图 (`system_architecture.mmd`)
展示了整个系统的分层架构，包括：
- 前端层 (Frontend)
- API网关层 (FastAPI)
- 业务逻辑层 (Business Logic)
- 适配器层 (Adapters)
- 数据存储层 (Data Layer)

### 2. PDF处理流水线图 (`pdf_processing_pipeline.mmd`)
详细展示了PDF文档处理的完整流程：
- 输入阶段：PDF文件格式检测
- 提取阶段：双路表格提取（Camelot + pdfplumber）
- 解析阶段：章节识别和J系列定位
- 标准化阶段：位段格式统一和单位转换
- 构建阶段：SIM模型构建
- 验证阶段：数据质量检查
- 输出阶段：YAML导出和数据库导入

### 3. 数据流架构图 (`data_flow.mmd`)
展示了多格式数据处理的完整流程：
- 多格式输入：PDF、XML、JSON、CSV
- 智能路由：格式检测和适配器选择
- 专用处理：各种格式的专用处理器
- 统一输出：SIM模型和YAML格式
- 数据持久化：数据库和文件存储

### 4. API结构图 (`api_structure.mmd`)
展示了API的分层结构：
- 前端界面层
- API网关层
- 核心API模块
- 业务逻辑层
- 数据访问层
- 数据存储

### 5. 部署架构图 (`deployment_architecture.mmd`)
展示了生产环境的部署架构：
- 负载均衡层
- Web服务层
- 应用服务层
- 微服务层
- 数据服务层
- 存储层
- 监控层

### 6. 技术栈架构图 (`technology_stack.mmd`)
展示了系统使用的技术栈：
- 前端技术栈：React、TypeScript、Vite等
- 后端技术栈：FastAPI、Python、Uvicorn等
- PDF处理技术栈：PyMuPDF、pdfplumber、Camelot等
- 数据处理技术栈：pandas、numpy、PyYAML等
- 数据库技术栈：MySQL、Redis等
- 部署技术栈：Docker、Kubernetes等
- 监控技术栈：Prometheus、Grafana等
- 开发工具栈：Git、ESLint、pytest等

### 7. 数据库架构图 (`database_architecture.mmd`) ⭐ 新增
详细展示了微服务数据库架构：
- 微服务层：7个独立的微服务，每个服务对应专用数据库
- 数据库实例层：7个独立的MySQL数据库实例，端口分离
- 数据表结构：每个数据库的详细表结构设计
- 缓存层：Redis多DB实例，按服务分离缓存
- 数据一致性：事件总线、Saga模式、CQRS模式

## 🚀 如何使用

### 在线查看
1. 访问 [Mermaid Live Editor](https://mermaid.live/)
2. 复制对应的 `.mmd` 文件内容
3. 粘贴到编辑器中查看图表

### 本地生成
1. 安装 Mermaid CLI：
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

2. 生成图片：
   ```bash
   mmdc -i system_overview.mmd -o system_overview.png
   mmdc -i core_value_proposition.mmd -o core_value_proposition.png
   mmdc -i system_architecture.mmd -o system_architecture.png
   mmdc -i pdf_processing_pipeline.mmd -o pdf_processing_pipeline.png
   mmdc -i data_flow.mmd -o data_flow.png
   mmdc -i api_structure.mmd -o api_structure.png
   mmdc -i deployment_architecture.mmd -o deployment_architecture.png
   mmdc -i technology_stack.mmd -o technology_stack.png
   mmdc -i database_architecture.mmd -o database_architecture.png
   ```

### 在文档中使用
这些图表可以嵌入到 Markdown 文档中：

```markdown
```mermaid
graph TB
    %% 复制 .mmd 文件内容到这里
```

## 📝 图表说明

### 颜色编码
- 🔵 蓝色：前端相关组件
- 🟣 紫色：API和网关组件
- 🟢 绿色：业务逻辑组件
- 🟠 橙色：适配器和处理组件
- 🔴 红色：数据存储组件
- 🟡 黄色：监控和工具组件

### 连接线说明
- 实线：直接调用关系
- 虚线：可选或反馈关系
- 粗线：主要数据流

## 🔧 自定义修改

如需修改图表，请：
1. 编辑对应的 `.mmd` 文件
2. 使用 Mermaid 语法
3. 保持颜色编码的一致性
4. 更新本 README 文档

## 📚 相关文档

- [Mermaid 官方文档](https://mermaid-js.github.io/mermaid/)
- [Mermaid 语法指南](https://mermaid-js.github.io/mermaid/#/flowchart)
- [6016-app 项目文档](../README_PDF_SYSTEM.md)
- [系统架构文档](../SYSTEM_ARCHITECTURE_OVERVIEW.md)

---

**注意**：这些图表展示了系统的设计架构，实际实现可能会有细微差异。请参考源代码获取最新的实现细节。

# 6016b - 语义互操作性系统

这是一个用于处理各种数据格式（PDF、MQTT、Link16、MAVLink等）的语义互操作性系统。

## 项目结构

- **backend/**: 后端服务，包含各种API和处理器
- **frontend/**: React + TypeScript 前端应用
- **microservices/**: 微服务配置文件
- **demo_*.py**: 各种演示脚本

## 主要功能

1. PDF处理和分析
2. MQTT消息适配
3. Link16数据处理
4. MAVLink协议支持
5. 语义互操作性和本体映射
6. RAG (检索增强生成) 服务

## 技术栈

- Python (后端)
- React + TypeScript (前端)
- FastAPI
- MQTT
- YAML配置
- Docker支持

## 部署

查看 `DEPLOYMENT_GUIDE.md` 了解详细部署说明。

## 开发

查看各个模块的文档：
- `PDF_PROCESSING_GUIDE.md` - PDF处理指南
- `MQTT_PIPELINE_GUIDE.md` - MQTT管道指南
- `UNIVERSAL_IMPORT_GUIDE.md` - 通用导入指南
- `SEMANTIC_INTEROPERABILITY_GUIDE.md` - 语义互操作性指南

## 许可证

详见项目许可证文件

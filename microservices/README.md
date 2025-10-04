# MIL-STD-6016 微服务架构

## 🎯 架构概述

本微服务架构将原有的单体应用拆分为多个独立的微服务，每个服务负责特定的业务领域，通过API网关统一对外提供服务。

## 🏗️ 服务架构

### 核心业务服务
- **pdf-service**: PDF文档处理服务
- **semantic-service**: 语义互操作服务
- **cdm-service**: CDM四层法服务
- **import-service**: 统一导入服务

### 支撑服务
- **user-service**: 用户管理服务
- **config-service**: 配置管理服务
- **monitor-service**: 监控告警服务
- **storage-service**: 文件存储服务

### 基础设施服务
- **api-gateway**: API网关
- **service-registry**: 服务注册发现
- **message-broker**: 消息队列
- **database**: 数据库集群

## 🚀 快速开始

### 使用Docker Compose启动
```bash
cd microservices
docker-compose up -d
```

### 使用Kubernetes部署
```bash
kubectl apply -f k8s/
```

## 📊 服务通信

### 同步通信
- REST API (HTTP/HTTPS)
- gRPC (高性能内部通信)

### 异步通信
- RabbitMQ (消息队列)
- Redis Pub/Sub (实时通知)

## 🔧 开发指南

### 服务开发
1. 每个服务独立开发、测试、部署
2. 使用统一的API规范
3. 实现健康检查和监控指标
4. 支持配置热更新

### 数据管理
1. 每个服务拥有独立数据库
2. 通过事件驱动实现数据一致性
3. 使用Saga模式处理分布式事务

## 📈 监控和运维

### 监控指标
- 服务健康状态
- 性能指标 (QPS, 延迟, 错误率)
- 资源使用情况
- 业务指标

### 日志管理
- 集中式日志收集
- 结构化日志格式
- 分布式链路追踪

## 🔒 安全策略

### 认证授权
- JWT Token认证
- RBAC权限控制
- API访问限流

### 网络安全
- 服务间TLS加密
- 网络隔离
- 安全扫描

## 📚 文档

- [API文档](./docs/api/)
- [部署指南](./docs/deployment/)
- [开发指南](./docs/development/)
- [运维手册](./docs/operations/)

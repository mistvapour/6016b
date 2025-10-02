# PDF处理系统部署指南

## 🚀 快速开始

### 1. 一键部署（推荐）

```bash
# 完整部署
./deploy.sh deploy

# 查看服务状态
./deploy.sh status

# 查看日志
./deploy.sh logs
```

### 2. 访问系统

- **前端界面**: http://localhost
- **API文档**: http://localhost/api/docs
- **健康检查**: http://localhost/health

## 📋 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **网络**: 100Mbps

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 50GB 可用空间
- **网络**: 1Gbps

### 软件依赖
- Docker 20.10+
- Docker Compose 2.0+
- Git

## 🔧 详细部署步骤

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd 6016-app

# 检查依赖
./deploy.sh help
```

### 2. 配置环境

```bash
# 创建环境配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

**重要配置项**:
```env
# 数据库配置
DB_ROOT_PASSWORD=your_secure_password
DB_USER=milstd6016
DB_PASSWORD=your_db_password

# 安全配置
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# 应用配置
ENVIRONMENT=production
MAX_WORKERS=4
MAX_FILE_SIZE=50
```

### 3. 部署服务

```bash
# 完整部署
./deploy.sh deploy

# 或者分步部署
./deploy.sh deploy --no-build  # 不重新构建镜像
./deploy.sh deploy --no-init   # 不初始化数据库
```

### 4. 验证部署

```bash
# 检查服务状态
./deploy.sh status

# 查看服务日志
./deploy.sh logs backend
./deploy.sh logs frontend
./deploy.sh logs mysql
```

## 🛠️ 管理命令

### 服务管理

```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看状态
./deploy.sh status
```

### 日志管理

```bash
# 查看所有日志
./deploy.sh logs

# 查看特定服务日志
./deploy.sh logs backend
./deploy.sh logs frontend
./deploy.sh logs mysql
./deploy.sh logs nginx

# 实时查看日志
docker-compose logs -f backend
```

### 数据管理

```bash
# 备份数据
./deploy.sh backup

# 恢复数据
./deploy.sh restore backup_20240101_120000

# 清理资源
./deploy.sh cleanup
```

## 🔒 安全配置

### 1. 数据库安全

```bash
# 修改数据库密码
docker-compose exec mysql mysql -u root -p
ALTER USER 'root'@'%' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

### 2. 应用安全

```bash
# 生成新的密钥
openssl rand -hex 32  # 用于SECRET_KEY
openssl rand -hex 32  # 用于JWT_SECRET_KEY
```

### 3. 网络安全

```bash
# 配置防火墙
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 3306/tcp  # 禁止外部访问数据库
ufw deny 6379/tcp  # 禁止外部访问Redis
```

### 4. SSL证书配置

```bash
# 创建SSL证书目录
mkdir -p ssl

# 生成自签名证书（测试用）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem

# 配置HTTPS（编辑nginx.conf）
```

## 📊 监控和维护

### 1. 系统监控

```bash
# 查看资源使用情况
docker stats

# 查看磁盘使用情况
df -h

# 查看内存使用情况
free -h
```

### 2. 日志监控

```bash
# 查看错误日志
tail -f logs/error.log

# 查看访问日志
tail -f logs/access.log

# 查看PDF处理日志
tail -f logs/pdf_processing.log
```

### 3. 性能优化

```bash
# 调整工作进程数
export MAX_WORKERS=8

# 调整文件上传大小
export MAX_FILE_SIZE=100

# 调整超时时间
export PDF_PROCESSING_TIMEOUT=600
```

## 🔄 更新和升级

### 1. 应用更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署
./deploy.sh deploy

# 或者只更新特定服务
docker-compose build backend
docker-compose up -d backend
```

### 2. 数据库迁移

```bash
# 备份当前数据
./deploy.sh backup

# 运行迁移脚本
docker-compose exec backend python migrate.py

# 验证迁移结果
docker-compose exec mysql mysql -u root -p -e "USE milstd6016; SHOW TABLES;"
```

## 🚨 故障排除

### 1. 常见问题

**问题**: 服务启动失败
```bash
# 检查日志
./deploy.sh logs

# 检查端口占用
netstat -tulpn | grep :8000

# 重启服务
./deploy.sh restart
```

**问题**: 数据库连接失败
```bash
# 检查数据库状态
docker-compose exec mysql mysqladmin ping

# 检查数据库日志
./deploy.sh logs mysql

# 重置数据库
docker-compose down -v
docker-compose up -d mysql
```

**问题**: 文件上传失败
```bash
# 检查文件权限
ls -la uploads/

# 检查磁盘空间
df -h

# 调整文件大小限制
export MAX_FILE_SIZE=100
```

### 2. 日志分析

```bash
# 查看错误日志
grep "ERROR" logs/app.log

# 查看PDF处理日志
grep "PDF处理" logs/pdf_processing.log

# 查看数据库操作日志
grep "数据库操作" logs/database.log
```

### 3. 性能问题

```bash
# 查看CPU使用情况
top -p $(pgrep -f "uvicorn")

# 查看内存使用情况
ps aux | grep uvicorn

# 查看磁盘I/O
iostat -x 1
```

## 📈 扩展和定制

### 1. 添加新的PDF标准

```python
# 在 backend/pdf_adapter/parse_sections.py 中添加新的解析规则
# 在 backend/pdf_adapter/normalize_bits.py 中添加新的标准化规则
```

### 2. 自定义校验规则

```python
# 在 backend/pdf_adapter/validators.py 中添加新的校验器
# 在 backend/pdf_adapter/validators.py 中更新 ComprehensiveValidator
```

### 3. 添加新的API接口

```python
# 在 backend/main.py 中添加新的路由
# 在 frontend/src/components/ 中添加新的组件
```

## 📞 支持和维护

### 1. 技术支持

- **文档**: 查看项目README和API文档
- **日志**: 检查系统日志获取详细错误信息
- **监控**: 使用系统监控工具检查资源使用情况

### 2. 定期维护

```bash
# 每日检查
./deploy.sh status
df -h
docker system df

# 每周维护
./deploy.sh backup
docker system prune -f
./deploy.sh logs | grep ERROR

# 每月维护
docker-compose pull
./deploy.sh deploy
```

### 3. 紧急恢复

```bash
# 快速恢复
./deploy.sh stop
./deploy.sh restore latest_backup
./deploy.sh start

# 完全重建
./deploy.sh cleanup
./deploy.sh deploy
```

## 📋 检查清单

### 部署前检查
- [ ] 系统要求满足
- [ ] 依赖软件已安装
- [ ] 配置文件已正确设置
- [ ] 网络端口已开放
- [ ] 磁盘空间充足

### 部署后检查
- [ ] 所有服务正常运行
- [ ] 数据库连接正常
- [ ] API接口可访问
- [ ] 前端界面可访问
- [ ] 文件上传功能正常
- [ ] PDF处理功能正常

### 生产环境检查
- [ ] 安全配置已设置
- [ ] 监控系统已配置
- [ ] 备份策略已实施
- [ ] 日志轮转已配置
- [ ] 性能优化已应用

---

**注意**: 本指南适用于生产环境部署。开发环境请参考 `README_PDF_SYSTEM.md` 中的开发指南。

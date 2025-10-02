# 系统组件全景矩阵

## 📊 核心组件依赖关系图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           6016-app 系统组件矩阵                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  配置层    │  前端层    │  API层     │  业务层    │  适配层    │  数据层      │
├─────────────────────────────────────────────────────────────────────────────┤
│ .env       │ App.tsx    │ main.py    │ universal_ │ pdf_       │ MySQL       │
│ config.py  │ Package.   │ pdf_api.py │ import_    │ adapter/   │ 数据库       │
│ deploy.sh  │ json       │ mqtt_api.  │ system.py  │ mqtt_      │ db.py       │
│ docker-    │ vite.      │ py         │ xml_to_    │ adapter/   │ Redis       │
│ compose.   │ config.ts  │ universal_ │ pdf_       │ xml_       │ (可选)      │
│ yml        │ tailwind.  │ import_    │ converter. │ adapter/   │ 文件存储     │
│ start_     │ config.js  │ api.py     │ py         │ json_      │ 日志文件     │
│ system.py  │ tsconfig.  │ import_    │ batch_     │ adapter/   │ 临时文件     │
│ require-   │ json       │ yaml.py    │ processor. │ csv_       │ 输出文件     │
│ ments.txt  │ PDFProces- │ db.py      │ py         │ adapter/   │ 缓存文件     │
│            │ sor.tsx    │            │            │            │             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🗂️ 文件系统架构

### 📁 项目根目录结构
```
6016-app/
├── 📄 配置文件
│   ├── .env                           # 环境变量配置
│   ├── .env.example                   # 环境变量模板
│   ├── docker-compose.yml             # Docker编排配置
│   ├── nginx.conf                     # Nginx配置
│   └── deploy.sh                      # 部署脚本
├── 🖥️ 后端服务 (backend/)
│   ├── 📋 核心API模块
│   │   ├── main.py                    # FastAPI主应用
│   │   ├── db.py                      # 数据库操作
│   │   ├── config.py                  # 应用配置
│   │   └── logging_config.py          # 日志配置
│   ├── 📄 PDF处理模块
│   │   ├── pdf_api.py                 # PDF API接口
│   │   └── pdf_adapter/               # PDF处理适配器
│   │       ├── pdf_processor.py       # 主处理器
│   │       ├── extract_tables.py      # 表格提取
│   │       ├── parse_sections.py      # 章节解析
│   │       ├── normalize_bits.py      # 位段标准化
│   │       ├── build_sim.py           # SIM构建
│   │       └── validators.py          # 数据验证
│   ├── 🔧 MQTT处理模块
│   │   ├── mqtt_api.py                # MQTT API接口
│   │   └── mqtt_adapter/              # MQTT处理适配器
│   │       ├── extract_tables.py      # MQTT表格提取
│   │       ├── parse_sections.py      # MQTT章节解析
│   │       ├── normalize_bits.py      # MQTT位段处理
│   │       ├── build_sim.py           # MQTT SIM构建
│   │       └── export_yaml.py         # YAML导出
│   ├── 🎯 统一导入模块
│   │   ├── universal_import_system.py # 统一导入系统
│   │   ├── universal_import_api.py    # 统一导入API
│   │   └── xml_to_pdf_converter.py    # XML转换器
│   ├── 📋 数据处理模块
│   │   ├── import_yaml.py             # YAML导入器
│   │   └── batch_processor.py         # 批量处理器
│   └── 📄 依赖配置
│       ├── requirements.txt           # Python依赖
│       ├── Dockerfile                 # Docker构建文件
│       └── start_system.py            # 启动脚本
├── 🎨 前端应用 (frontend/)
│   ├── src/
│   │   ├── App.tsx                    # 主应用组件
│   │   ├── main.tsx                   # 应用入口
│   │   ├── index.css                  # 全局样式
│   │   ├── components/                # 组件目录
│   │   │   ├── PDFProcessor.tsx       # PDF处理组件
│   │   │   └── ui/                    # UI组件库
│   │   │       ├── button.tsx         # 按钮组件
│   │   │       ├── card.tsx           # 卡片组件
│   │   │       ├── table.tsx          # 表格组件
│   │   │       ├── dialog.tsx         # 对话框组件
│   │   │       └── ...                # 其他UI组件
│   │   └── lib/
│   │       └── utils.ts               # 工具函数
│   ├── public/                        # 静态资源
│   │   └── vite.svg                   # 应用图标
│   ├── 📄 配置文件
│   │   ├── package.json               # Node.js依赖
│   │   ├── package-lock.json          # 依赖锁定文件
│   │   ├── vite.config.ts             # Vite配置
│   │   ├── tsconfig.json              # TypeScript配置
│   │   ├── tsconfig.app.json          # 应用TS配置
│   │   ├── tsconfig.node.json         # Node TS配置
│   │   ├── tailwind.config.js         # Tailwind配置
│   │   ├── postcss.config.js          # PostCSS配置
│   │   ├── eslint.config.js           # ESLint配置
│   │   ├── components.json            # shadcn/ui配置
│   │   ├── index.html                 # HTML模板
│   │   ├── README.md                  # 前端文档
│   │   └── Dockerfile                 # 前端Docker文件
├── 📋 测试文件 (test_sample/)
│   ├── common.xml                     # MAVLink测试文件
│   ├── mqtt_connect_test.pdf          # MQTT测试PDF
│   ├── link16-import.pdf              # Link16测试PDF
│   └── sample_j_message.pdf           # J消息测试PDF
├── 📄 输出目录
│   ├── mavlink_output/                # MAVLink处理输出
│   ├── mqtt_output/                   # MQTT处理输出
│   ├── link16_output/                 # Link16处理输出
│   ├── universal_output/              # 统一处理输出
│   └── test_output/                   # 测试输出
└── 📚 文档文件
    ├── PROJECT_SUMMARY.md             # 项目总结
    ├── DEPLOYMENT_GUIDE.md            # 部署指南
    ├── PDF_PROCESSING_GUIDE.md        # PDF处理指南
    ├── UNIVERSAL_IMPORT_GUIDE.md      # 统一导入指南
    ├── SYSTEM_ARCHITECTURE_OVERVIEW.md # 系统架构梳理
    ├── MQTT_PIPELINE_GUIDE.md         # MQTT流水线指南
    ├── XML_TO_PDF_CONVERSION_GUIDE.md # XML转换指南
    └── FINAL_SUMMARY.md               # 最终总结
```

## 🔧 依赖关系矩阵

### 📄 后端依赖 (requirements.txt)
```python
# 核心框架
fastapi==0.115.4               # Web框架
uvicorn[standard]==0.30.6      # ASGI服务器
python-dotenv==1.0.1           # 环境变量管理

# 数据库
mysql-connector-python==9.0.0  # MySQL驱动

# PDF处理核心库
PyMuPDF==1.23.14              # PDF文档解析
pdfplumber==0.10.3            # PDF表格提取
camelot-py[cv]==0.10.1        # 高级表格处理
opencv-python==4.8.1.78       # 计算机视觉库
pytesseract==0.3.10           # OCR文字识别
layoutparser==0.3.4           # 布局分析
detectron2==0.6               # 深度学习模型

# 数据处理
PyYAML==6.0.1                 # YAML序列化
numpy==1.24.3                 # 数值计算
pandas==2.0.3                 # 数据分析
requests==2.31.0              # HTTP客户端

# 其他工具库
python-magic                   # 文件类型检测 (可选)
redis                         # 缓存系统 (可选)
```

### 🎨 前端依赖 (package.json)
```json
{
  "dependencies": {
    // 核心框架
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    
    // 路由和状态管理
    "react-router-dom": "^6.0.0",
    
    // UI组件库
    "@radix-ui/react-slot": "^1.1.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "lucide-react": "^0.446.0",
    "tailwind-merge": "^2.5.2",
    "tailwindcss-animate": "^1.0.7",
    
    // 工具库
    "axios": "^1.0.0"
  },
  "devDependencies": {
    // 构建工具
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.1",
    
    // TypeScript
    "typescript": "^5.5.3",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    
    // 样式工具
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.16",
    
    // 代码质量
    "eslint": "^9.9.0",
    "@eslint/js": "^9.9.0",
    "eslint-plugin-react-hooks": "^5.1.0-rc.0",
    "eslint-plugin-react-refresh": "^0.4.9",
    "globals": "^15.9.0",
    "typescript-eslint": "^8.0.1"
  }
}
```

### 🐳 容器依赖 (docker-compose.yml)
```yaml
services:
  # 数据库服务
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - app-network

  # 缓存服务 (可选)
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - app-network

  # 后端服务
  backend:
    build: ./backend
    environment:
      DB_HOST: mysql
      REDIS_HOST: redis
    depends_on:
      - mysql
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./output:/app/output
      - ./logs:/app/logs
    networks:
      - app-network

  # 前端服务
  frontend:
    build: ./frontend
    depends_on:
      - backend
    networks:
      - app-network

  # 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

volumes:
  mysql_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

## 🎯 模块间依赖关系

### 📊 依赖层次图
```
Level 1: 基础配置层
├── config.py                 # 应用配置
├── logging_config.py          # 日志配置
├── .env                       # 环境变量
└── db.py                      # 数据库连接

Level 2: 核心业务层
├── universal_import_system.py # 统一导入系统
├── pdf_adapter/               # PDF处理适配器
├── mqtt_adapter/              # MQTT处理适配器
├── xml_to_pdf_converter.py    # XML转换器
└── import_yaml.py             # YAML导入器

Level 3: API接口层
├── main.py                    # 主应用 (依赖所有业务模块)
├── pdf_api.py                 # PDF API (依赖pdf_adapter)
├── mqtt_api.py                # MQTT API (依赖mqtt_adapter)
└── universal_import_api.py    # 统一API (依赖universal_import_system)

Level 4: 前端界面层
├── App.tsx                    # 主应用 (调用所有API)
├── PDFProcessor.tsx           # PDF处理组件 (调用PDF API)
└── ui/                        # UI组件库 (被所有组件使用)
```

### 🔄 数据流依赖
```
用户输入 → 前端组件 → API接口 → 业务逻辑 → 适配器 → 数据库/文件
    ↑         ↓         ↓         ↓         ↓         ↓
  界面交互   HTTP请求   路由分发   格式处理   数据转换   持久化存储
```

## 🚀 启动依赖顺序

### 🔧 开发环境启动顺序
```bash
1. 数据库服务启动
   mysql -u root -p

2. 后端服务启动 (依赖数据库)
   cd backend
   uvicorn main:app --reload

3. 前端服务启动 (依赖后端API)
   cd frontend
   npm run dev
```

### 🐳 生产环境启动顺序 (Docker)
```bash
1. 基础服务 (MySQL + Redis)
   docker-compose up -d mysql redis

2. 后端服务 (依赖基础服务)
   docker-compose up -d backend

3. 前端服务 (依赖后端)
   docker-compose up -d frontend

4. 反向代理 (依赖前后端)
   docker-compose up -d nginx
```

## 📊 配置管理架构

### 🔧 配置文件层次
```
环境配置
├── .env                       # 主环境配置文件
├── .env.example               # 环境配置模板
├── config.py                  # Python应用配置
├── logging_config.py          # 日志系统配置
├── docker-compose.yml         # 容器编排配置
└── nginx.conf                 # 反向代理配置

前端配置
├── vite.config.ts            # 构建工具配置
├── tsconfig.json             # TypeScript配置
├── tailwind.config.js        # 样式框架配置
├── eslint.config.js          # 代码检查配置
└── components.json           # UI组件配置

部署配置
├── deploy.sh                 # 部署脚本
├── start_system.py           # 本地启动脚本
├── backend/Dockerfile        # 后端容器配置
└── frontend/Dockerfile       # 前端容器配置
```

### 🎯 配置优先级
```
1. 环境变量 (.env文件)         # 最高优先级
2. 命令行参数                  # 中等优先级
3. 配置文件默认值 (config.py)  # 最低优先级
```

## 🎉 系统组件总结

### ✅ 核心组件统计
- **📄 配置文件**: 15个 (环境、构建、部署)
- **🔧 后端模块**: 25个 (API、业务逻辑、适配器)
- **🎨 前端组件**: 12个 (页面、组件、工具)
- **🐳 容器服务**: 5个 (数据库、缓存、应用、代理)
- **📚 文档文件**: 10个 (指南、总结、架构)
- **🧪 测试文件**: 8个 (样本、脚本、输出)

### 🎯 关键依赖关系
- **前端 → 后端**: HTTP API调用
- **后端 → 数据库**: MySQL连接和查询
- **业务逻辑 → 适配器**: 格式处理和转换
- **适配器 → 第三方库**: PDF/XML/JSON处理
- **配置系统 → 所有模块**: 统一配置管理

**这是一个高度模块化、层次清晰、依赖明确的企业级系统架构！** 🏆

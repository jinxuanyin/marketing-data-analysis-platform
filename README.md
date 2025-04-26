# 营销大数据分析与可视化平台

基于Python (FastAPI) + React + Tailwind CSS的营销数据分析平台，提供用户聚类分析、行为热力图和转化漏斗分析等功能。

## 功能特点

- **数据清洗**：自动检测并清理CSV文件中的脏数据、缺失值和异常值
- **K-means用户聚类**：对用户行为数据进行标准化和聚类分析，生成二维散点图
- **用户行为热力图**：生成热力图，展示用户行为频率，横轴为行为事件，纵轴为用户ID
- **用户转化漏斗图**：自动识别用户行为转化流程，生成漏斗图展示各阶段转化率

## 项目结构

```
marketing_data_analysis_platform/
├── backend/                     # 后端代码
│   ├── clean_data.py            # 数据清洗脚本
│   ├── kmeans_cluster_analysis.py # K-means聚类分析脚本
│   ├── draw_heatmap.py          # 用户行为热力图生成脚本
│   ├── funnel_analysis_funnel_shape.py # 用户转化漏斗图生成脚本
│   ├── main.py                  # FastAPI主文件
│   └── requirements.txt         # 后端依赖
├── frontend/                    # 前端代码
│   ├── public/                  # 静态文件
│   ├── src/                     # React源代码
│   │   ├── components/          # 组件
│   │   ├── pages/               # 页面
│   │   ├── App.js               # 应用入口
│   │   └── index.js             # 主入口
│   ├── package.json             # 前端依赖
│   └── tailwind.config.js       # Tailwind CSS配置
└── README.md                    # 项目说明
```

## 环境要求

- Python 3.8+
- Node.js 14+
- npm 6+

## 安装与运行

### 后端

1. 进入后端目录
```bash
cd marketing_data_analysis_platform/backend
```

2. 创建虚拟环境（可选但推荐）
```bash
python -m venv venv
```

3. 激活虚拟环境
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 运行服务器
```bash
uvicorn main:app --reload
```

服务器将在 http://localhost:8000 运行，API文档可在 http://localhost:8000/docs 查看。

### 前端

1. 进入前端目录
```bash
cd marketing_data_analysis_platform/frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm start
```

前端应用将在 http://localhost:3000 运行。

## 使用方法

1. 准备CSV格式的用户行为数据，确保包含"是否脏数据"列
2. 访问 http://localhost:3000 并上传数据文件
3. 等待系统完成分析（通常需要10-30秒，取决于数据量大小）
4. 查看分析结果，包括用户聚类图、行为热力图和转化漏斗图

## 生产环境部署

### 后端

1. 在生产环境使用Gunicorn作为WSGI服务器
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

2. 配置Nginx或Apache作为反向代理（可选）

### 前端

1. 构建生产版本
```bash
npm run build
```

2. 将build目录下的文件部署到静态文件服务器或CDN

## 注意事项

- 上传的CSV文件必须包含"是否脏数据"列，用于数据清洗步骤
- 大数据文件（>100MB）可能需要更长的处理时间
- 在生产环境中，应该配置适当的CORS策略和安全措施 
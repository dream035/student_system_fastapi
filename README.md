# 教务管理系统 API

基于 FastAPI + SQLAlchemy 2.0 异步的学生管理系统。

## 功能特点

- ✅ 学生信息的增删改查
- ✅ 批量删除学生
- ✅ 按姓名模糊搜索
- ✅ 成绩统计分析
- ✅ 异步数据库操作
- ✅ 自动生成 API 文档

## 快速开始

### 1. 克隆项目

```bash
git clone <你的仓库地址>
cd student_system_fastapi
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

修改 `.env` 文件中的数据库连接：

```env
DATABASE_URL=mysql+aiomysql://root:你的密码@localhost:3306/student_system
```

创建数据库：

```sql
CREATE DATABASE student_system CHARACTER SET utf8mb4;
```

### 5. 运行项目

```bash
uvicorn app.main:app --reload
```

### 6. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/students/ | 添加学生 |
| GET | /api/v1/students/ | 获取所有学生 |
| GET | /api/v1/students/{id} | 获取单个学生 |
| PUT | /api/v1/students/{id} | 更新学生 |
| DELETE | /api/v1/students/{id} | 删除学生 |
| DELETE | /api/v1/students/batch/ | 批量删除 |
| GET | /api/v1/students/search/ | 搜索学生 |
| GET | /api/v1/students/stats/ | 统计信息 |

## 项目结构

```
student_system_fastapi/
├── app/
│   ├── main.py          # 应用入口
│   ├── database.py      # 数据库配置
│   ├── models.py        # ORM模型
│   ├── schemas.py       # Pydantic模型
│   ├── routers/         # 路由层
│   └── crud/            # 数据操作层
├── .env                 # 环境变量
└── requirements.txt     # 依赖
```

## 示例请求

### 添加学生

```bash
curl -X POST "http://localhost:8000/api/v1/students/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "chinese": 85.5,
    "math": 90.0,
    "english": 88.0
  }'
```

### 获取所有学生。

```bash
curl "http://localhost:8000/api/v1/students/?page=1&page_size=10"
```

## 技术栈

- **FastAPI** - Web框架
- **SQLAlchemy 2.0** - 异步ORM
- **aiomysql** - MySQL异步驱动
- **Pydantic v2** - 数据验证

## 许可证

MIT License
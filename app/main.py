# FastAPI 主入口
# app/main.py
"""
FastAPI 应用主入口
创建应用、注册路由、配置中间件
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .database import create_tables, async_engine
from .routers import students_router

# 加载环境变量
load_dotenv()

# 应用配置
APP_NAME = os.getenv("APP_NAME", "教务管理系统")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时：
        - 创建数据库表
        - 初始化其他资源

    关闭时：
        - 关闭数据库连接
        - 清理资源
    """
    # 启动时执行
    print(f"🚀 正在启动 {APP_NAME} v{APP_VERSION}...")
    print("📊 检查数据库表...")
    await create_tables()
    print("✅ 数据库表准备就绪")

    yield  # 应用运行期间

    # 关闭时执行
    print("👋 正在关闭应用...")
    await async_engine.dispose()
    print("✅ 资源已清理")


# 创建 FastAPI 应用
app = FastAPI(
    title=APP_NAME,
    description=APP_NAME + " API 文档",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,  # 生产环境可关闭文档
    redoc_url="/redoc" if DEBUG else None
)

# 配置 CORS 中间件（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(students_router)


# ============= 全局异常处理 =============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "detail": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if DEBUG else None
        }
    )


# ============= 健康检查 =============

@app.get(
    "/",
    tags=["系统"],
    summary="根路径",
    description="API 根路径，返回基本信息"
)
async def root():
    """API 根路径"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get(
    "/health",
    tags=["系统"],
    summary="健康检查",
    description="检查服务是否正常运行"
)
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION
    }
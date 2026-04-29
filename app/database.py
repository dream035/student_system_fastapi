# 数据库配置
# app/database.py
# app/database.py
"""
数据库配置模块
负责：创建数据库引擎、会话工厂、依赖注入
"""
from contextlib import asynccontextmanager
from datetime import datetime
import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, DateTime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接URL（从环境变量读取）
DATABASE_URL = os.getenv("DATABASE_URL")

# 创建异步引擎
async_engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",  # 调试模式打印SQL
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_pre_ping=True,  # 使用前检查连接
    pool_recycle=3600  # 连接回收时间（秒）
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False  # 提交后不过期对象
)


# 定义模型基类
class Base(DeclarativeBase):
    """
    模型基类
    所有模型都会自动包含 create_time 和 update_time 字段
    """
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),  # 数据库默认值
        default=func.now(),  # Python默认值
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),  # 更新时自动修改
        comment="修改时间"
    )


async def get_database() -> AsyncSession:
    """
    依赖注入函数：获取数据库会话

    用法：
        @router.get("/")
        async def get_data(db: AsyncSession = Depends(get_database)):
            ...

    特点：
        - 自动管理事务（成功提交，失败回滚）
        - 自动关闭会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # 无异常则提交
        except Exception:
            await session.rollback()  # 有异常则回滚
            raise
        finally:
            await session.close()  # 关闭会话


async def create_tables():
    """
    创建数据库表
    在应用启动时调用
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建/检查完成")


async def drop_tables():
    """
    删除所有表（仅用于测试）
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("⚠️ 所有表已删除")


@asynccontextmanager
async def get_db_session():
    """
    手动获取会话的上下文管理器
    用于非FastAPI依赖注入的场景
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
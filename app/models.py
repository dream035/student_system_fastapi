#数据模型
# app/models.py
# app/models.py
"""
数据库模型定义
每个类对应数据库中的一张表
"""
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Index
from .database import Base


class StudentDB(Base):
    """
    学生表模型

    对应数据库表：students
    字段：
        - id: 主键，自增
        - name: 姓名，唯一，非空
        - chinese: 语文成绩
        - math: 数学成绩
        - english: 英语成绩
        - create_time: 创建时间（继承自Base）
        - update_time: 修改时间（继承自Base）
    """
    __tablename__ = "students"

    # 联合索引：按姓名和创建时间查询优化
    __table_args__ = (
        Index('idx_name_create_time', 'name', 'create_time'),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="学生ID"
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="学生姓名"
    )

    chinese: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="语文成绩"
    )

    math: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="数学成绩"
    )

    english: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="英语成绩"
    )

    def __repr__(self) -> str:
        """调试用字符串表示"""
        return f"<Student(id={self.id}, name={self.name}, chinese={self.chinese}, math={self.math}, english={self.english})>"

    def to_dict(self) -> dict:
        """
        转换为字典格式
        用于响应序列化
        """
        return {
            "id": self.id,
            "name": self.name,
            "chinese": self.chinese,
            "math": self.math,
            "english": self.english,
            "total": self.chinese + self.math + self.english,
            "average": round((self.chinese + self.math + self.english) / 3, 2),
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }

    @property
    def total(self) -> float:
        """总分（属性方式访问）"""
        return self.chinese + self.math + self.english

    @property
    def average(self) -> float:
        """平均分"""
        return round(self.total / 3, 2)
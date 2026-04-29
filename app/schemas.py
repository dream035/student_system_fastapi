# Pydantic 模型（请求/响应）
# app/schemas.py
"""
Pydantic 模型定义
用于：请求数据验证、响应数据序列化
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============= 学生相关模型 =============

class StudentBase(BaseModel):
    """学生基础模型（公共字段）"""
    name: str = Field(..., min_length=1, max_length=50, description="学生姓名")
    chinese: float = Field(..., ge=0, le=100, description="语文成绩")
    math: float = Field(..., ge=0, le=100, description="数学成绩")
    english: float = Field(..., ge=0, le=100, description="英语成绩")


class StudentCreate(StudentBase):
    """创建学生请求模型"""

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """自定义姓名验证"""
        if not v.strip():
            raise ValueError('姓名不能为空')
        if len(v) > 50:
            raise ValueError('姓名不能超过50个字符')
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "张三",
                "chinese": 85.5,
                "math": 90.0,
                "english": 88.0
            }
        }
    )


class StudentUpdate(BaseModel):
    """更新学生请求模型（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="学生姓名")
    chinese: Optional[float] = Field(None, ge=0, le=100, description="语文成绩")
    math: Optional[float] = Field(None, ge=0, le=100, description="数学成绩")
    english: Optional[float] = Field(None, ge=0, le=100, description="英语成绩")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "张三丰",
                "chinese": 90.0
            }
        }
    )


class StudentResponse(BaseModel):
    """学生响应模型"""
    id: int
    name: str
    chinese: float
    math: float
    english: float
    total: float = Field(description="总分")
    average: float = Field(description="平均分")
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    """学生列表响应模型"""
    total: int = Field(description="总记录数")
    items: List[StudentResponse] = Field(description="学生列表")


# ============= 通用响应模型 =============

class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息")
    data: Optional[dict] = Field(None, description="数据")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": None
            }
        }
    )


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")


# ============= 统计相关模型 =============

class SubjectStats(BaseModel):
    """单科统计"""
    avg: float = Field(description="平均分")
    max: float = Field(description="最高分")
    min: float = Field(description="最低分")
    pass_rate: float = Field(description="及格率（%）")


class StatisticsResponse(BaseModel):
    """统计响应模型"""
    total_students: int = Field(description="学生总数")
    chinese: SubjectStats
    math: SubjectStats
    english: SubjectStats
    overall_avg: float = Field(description="总平均分")
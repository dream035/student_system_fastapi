# 学生相关路由
# app/routers/students.py
# app/routers/students.py
"""
学生管理路由
定义所有学生相关的 API 端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_database
from app.curd import StudentCRUD
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
    StatisticsResponse,
    SubjectStats,
    ResponseModel
)


# 创建路由器，添加统一前缀和标签
router = APIRouter(
    prefix="/api/v1/students",
    tags=["学生管理"]
)


# ============= POST 请求 =============

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="添加学生",
    description="创建一个新的学生记录"
)
async def create_student(
        student_data: StudentCreate,
        db: AsyncSession = Depends(get_database)
):
    """
    添加学生

    - **name**: 学生姓名（1-50字符）
    - **chinese**: 语文成绩（0-100）
    - **math**: 数学成绩（0-100）
    - **english**: 英语成绩（0-100）
    """
    # 检查姓名是否已存在
    existing = await StudentCRUD.get_by_name(db, student_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"学生 '{student_data.name}' 已存在"
        )

    # 创建学生
    new_student = await StudentCRUD.create(db, student_data)

    return new_student


# ============= GET 请求 =============

@router.get(
    "/",
    response_model=StudentListResponse,
    summary="获取学生列表",
    description="分页获取所有学生"
)
async def get_all_students(
        page: int = Query(1, ge=1, description="页数"),
        page_size: int = Query(10, ge=1, le=1000, description="每页数据量"),
        db: AsyncSession = Depends(get_database)
):
    """
    获取所有学生（分页）

    - **page**: 页数
    - **page_size**: 每页数据量
    """
    students, total = await StudentCRUD.get_all(db, page, page_size)

    return StudentListResponse(
        total=total,
        items=students
    )


@router.get(
    "/search/",
    response_model=StudentListResponse,
    summary="搜索学生",
    description="按姓名模糊搜索学生"
)
async def search_students(
        name: str = Query(..., min_length=1, description="搜索关键词"),
        page: int = Query(1, ge=1, description="页数"),
        page_size: int = Query(10, ge=1, le=1000, description="每页数据量"),
        db: AsyncSession = Depends(get_database)
):
    """
    按姓名搜索学生（模糊匹配）

    - **name**: 搜索关键词（如：'张' 会匹配 '张三'、'张四'）
    """
    students, total = await StudentCRUD.search_by_name(db, name, page, page_size)

    return StudentListResponse(
        total=total,
        items=students
    )


@router.get(
    "/stats/",
    response_model=StatisticsResponse,
    summary="获取统计信息",
    description="获取所有学生的成绩统计"
)
async def get_statistics(
        db: AsyncSession = Depends(get_database)
):
    """
    获取成绩统计信息

    包括：
    - 学生总数
    - 各科平均分、最高分、最低分、及格率
    - 总平均分
    """
    stats = await StudentCRUD.get_statistics(db)

    return StatisticsResponse(
        total_students=stats["total_students"],
        chinese=SubjectStats(**stats["chinese"]),
        math=SubjectStats(**stats["math"]),
        english=SubjectStats(**stats["english"]),
        overall_avg=stats["overall_avg"]
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="获取学生详情",
    description="根据ID获取单个学生信息"
)
async def get_student(
        student_id: int,
        db: AsyncSession = Depends(get_database)
):
    """
    根据学生ID获取详细信息
    """
    student = await StudentCRUD.get_by_id(db, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"学生 ID {student_id} 不存在"
        )

    return student


# ============= PUT 请求 =============

@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="更新学生",
    description="更新学生的部分或全部信息"
)
async def update_student(
        student_id: int,
        update_data: StudentUpdate,
        db: AsyncSession = Depends(get_database)
):
    """
    更新学生信息

    - 所有字段都是可选的，只更新提供的字段
    - 如果要更新姓名，会检查新姓名是否已被占用
    """
    # 如果要更新姓名，检查是否重复
    if update_data.name:
        existing = await StudentCRUD.get_by_name(db, update_data.name)
        if existing and existing.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"姓名 '{update_data.name}' 已被占用"
            )

    # 更新学生
    updated_student = await StudentCRUD.update(db, student_id, update_data)

    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"学生 ID {student_id} 不存在"
        )

    return updated_student


# ============= DELETE 请求 =============

@router.delete(
    "/{student_id}",
    response_model=ResponseModel,
    summary="删除学生",
    description="根据ID删除单个学生"
)
async def delete_student(
        student_id: int,
        db: AsyncSession = Depends(get_database)
):
    """
    删除指定ID的学生
    """
    deleted = await StudentCRUD.delete(db, student_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"学生 ID {student_id} 不存在"
        )

    return ResponseModel(
        code=200,
        message=f"学生 ID {student_id} 删除成功",
        data={"id": student_id}
    )


@router.delete(
    "/batch/",
    response_model=ResponseModel,
    summary="批量删除学生",
    description="批量删除多个学生"
)
async def delete_students_batch(
        student_ids: List[int] = Query(..., description="学生ID列表，用逗号分隔"),
        db: AsyncSession = Depends(get_database)
):
    """
    批量删除学生

    - **student_ids**: 要删除的学生ID列表，如：`?student_ids=1&student_ids=2&student_ids=3`
    """
    deleted_count = await StudentCRUD.delete_batch(db, student_ids)

    return ResponseModel(
        code=200,
        message=f"成功删除 {deleted_count} 名学生",
        data={"deleted_count": deleted_count, "ids": student_ids}
    )
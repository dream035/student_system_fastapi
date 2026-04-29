#学生数据库操作
# app/crud/student_crud.py
"""
学生数据操作层
封装所有与数据库的交互
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import StudentDB
from ..schemas import StudentCreate, StudentUpdate


class StudentCRUD:
    """学生数据操作类"""

    @staticmethod
    async def create(db: AsyncSession, student_data: StudentCreate) -> StudentDB:
        """
        创建学生

        Args:
            db: 数据库会话
            student_data: 学生创建数据

        Returns:
            创建的学生对象
        """
        # 创建模型实例
        new_student = StudentDB(
            name=student_data.name,
            chinese=student_data.chinese,
            math=student_data.math,
            english=student_data.english
        )

        # 添加到数据库
        db.add(new_student)
        await db.flush()  # 刷新获取ID
        await db.refresh(new_student)  # 刷新获取完整数据

        return new_student

    @staticmethod
    async def get_by_id(db: AsyncSession, student_id: int) -> Optional[StudentDB]:
        """
        根据ID获取学生

        Args:
            db: 数据库会话
            student_id: 学生ID

        Returns:
            学生对象或None
        """
        result = await db.execute(
            select(StudentDB).where(StudentDB.id == student_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[StudentDB]:
        """
        根据姓名获取学生（精确匹配）

        Args:
            db: 数据库会话
            name: 学生姓名

        Returns:
            学生对象或None
        """
        result = await db.execute(
            select(StudentDB).where(StudentDB.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
            db: AsyncSession,
            page: int = 1,
            page_size: int = 10
    ) -> Tuple[List[StudentDB], int]:
        """
        获取所有学生（分页）

        Args:
            db: 数据库会话
            page: 页数
            page_size: 返回记录数(每页数据量)

        Returns:
            (学生列表, 总记录数)
        """
        # 查询总数
        total_result = await db.execute(select(func.count()).select_from(StudentDB))
        total = total_result.scalar()

        # 查询分页数据
        skip = (page - 1) * page_size
        limit = page_size
        result = await db.execute(
            select(StudentDB)
            .offset(skip)
            .limit(limit)
            .order_by(StudentDB.id.asc())
        )
        students = result.scalars().all()

        return students, total

    @staticmethod
    async def search_by_name(
            db: AsyncSession,
            name: str,
            page: int = 1,
            page_size: int = 10
    ) -> Tuple[List[StudentDB], int]:
        """
        按姓名模糊搜索

        Args:
            db: 数据库会话
            name: 搜索关键词
            page: 页数
            page_size: 返回记录数(每页数据量)

        Returns:
            (学生列表, 总记录数)
        """
        # 构建查询条件
        condition = StudentDB.name.contains(name)

        # 查询总数
        total_result = await db.execute(
            select(func.count()).select_from(StudentDB).where(condition)
        )
        total = total_result.scalar()

        # 查询分页数据
        skip = (page - 1) * page_size
        limit = page_size
        result = await db.execute(
            select(StudentDB)
            .where(condition)
            .offset(skip)
            .limit(limit)
            .order_by(StudentDB.id.asc())
        )
        students = result.scalars().all()

        return students, total

    @staticmethod
    async def update(
            db: AsyncSession,
            student_id: int,
            update_data: StudentUpdate
    ) -> Optional[StudentDB]:
        """
        更新学生信息

        Args:
            db: 数据库会话
            student_id: 学生ID
            update_data: 更新数据

        Returns:
            更新后的学生对象或None
        """
        # 获取学生
        student = await StudentCRUD.get_by_id(db, student_id)
        if not student:
            return None

        # 只更新提供的字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(student, key, value)

        await db.flush()
        await db.refresh(student)

        return student

    @staticmethod
    async def delete(db: AsyncSession, student_id: int) -> bool:
        """
        删除学生

        Args:
            db: 数据库会话
            student_id: 学生ID

        Returns:
            是否删除成功
        """
        result = await db.execute(
            delete(StudentDB).where(StudentDB.id == student_id)
        )
        return result.rowcount > 0

    @staticmethod
    async def delete_batch(db: AsyncSession, student_ids: List[int]) -> int:
        """
        批量删除学生

        Args:
            db: 数据库会话
            student_ids: 学生ID列表

        Returns:
            删除的记录数
        """
        result = await db.execute(
            delete(StudentDB).where(StudentDB.id.in_(student_ids))
        )
        return result.rowcount

    @staticmethod
    async def get_statistics(db: AsyncSession) -> dict:
        """
        获取成绩统计信息

        Args:
            db: 数据库会话

        Returns:
            统计信息字典
        """
        # 获取所有学生
        result = await db.execute(select(StudentDB))
        students = result.scalars().all()

        if not students:
            return {
                "total_students": 0,
                "chinese": {"avg": 0, "max": 0, "min": 0, "pass_rate": 0},
                "math": {"avg": 0, "max": 0, "min": 0, "pass_rate": 0},
                "english": {"avg": 0, "max": 0, "min": 0, "pass_rate": 0},
                "overall_avg": 0
            }

        # 计算各科成绩
        chinese_scores = [s.chinese for s in students]
        math_scores = [s.math for s in students]
        english_scores = [s.english for s in students]

        # 计算及格率（>=60分）
        chinese_pass = sum(1 for s in chinese_scores if s >= 60) / len(students) * 100
        math_pass = sum(1 for s in math_scores if s >= 60) / len(students) * 100
        english_pass = sum(1 for s in english_scores if s >= 60) / len(students) * 100

        # 计算总分平均
        total_scores = [s.total for s in students]

        return {
            "total_students": len(students),
            "chinese": {
                "avg": round(sum(chinese_scores) / len(students), 2),
                "max": max(chinese_scores),
                "min": min(chinese_scores),
                "pass_rate": round(chinese_pass, 2)
            },
            "math": {
                "avg": round(sum(math_scores) / len(students), 2),
                "max": max(math_scores),
                "min": min(math_scores),
                "pass_rate": round(math_pass, 2)
            },
            "english": {
                "avg": round(sum(english_scores) / len(students), 2),
                "max": max(english_scores),
                "min": min(english_scores),
                "pass_rate": round(english_pass, 2)
            },
            "overall_avg": round(sum(total_scores) / len(students), 2)
        }
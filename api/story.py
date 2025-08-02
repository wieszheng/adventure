# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/30 23:04
@Author   : wieszheng
@Software : PyCharm
"""
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session

from core.story_generator import StoryGenerator
from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
)
from schemas.job import StoryJobResponse

router = APIRouter(
    prefix="/stories",
    tags=["故事"]
)


def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    """
    获取session id
    :param session_id:
    :return:
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("/create", response_model=StoryJobResponse)
def create_story(
        request: CreateStoryRequest,
        background_tasks: BackgroundTasks,
        response: Response,
        session_id: str = Depends(get_session_id),
        db: Session = Depends(get_db)
):
    """
    创建故事
    :param request: CreateStoryRequest对象，包含故事创建请求数据，主要是主题信息
    :param background_tasks:  BackgroundTasks对象，用于添加后台任务
    :param response: Response对象，用于设置响应相关的数据
    :param session_id: str类型，会话ID，通过依赖注入获取
    :param db: 数据库会话，通过依赖注入获取
    :return: StoryJobResponse对象，包含创建的故事任务信息
    """

    # 设置会话cookie
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    # 生成唯一任务ID并创建故事任务记录
    job_id = str(uuid.uuid4())

    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="pending"
    )
    db.add(job)
    db.commit()

    # 添加后台故事生成任务
    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )

    return job


def generate_story_task(job_id: str, theme: str, session_id: str):
    """
    生成故事任务
    该函数根据给定的任务ID、主题和会话ID来处理故事生成任务。它会查询数据库中的任务记录，
    更新任务状态，并调用故事生成器来创建故事内容。
    :param job_id: 故事任务ID
    :param theme: 故事主题
    :param session_id: 会话ID
    :return:
    """
    db = SessionLocal()

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

        if not job:
            return

        try:
            job.status = "processing"
            db.commit()

            story = StoryGenerator.generate_story(db, session_id, theme)

            job.story_id = story.id
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()
    finally:
        db.close()


@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    """
    获取完整的故事
    :param story_id: 故事ID
    :param db: 数据库会话
    :return: CompleteStoryResponse对象，包含完整的故事信息
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="故事未找到")

    complete_story = build_complete_story_tree(db, story)
    return complete_story


def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
    """
    构建完整的故事树结构响应对象

    该函数从数据库中查询指定故事的所有节点，构建完整的树形结构，
    并返回包含根节点和所有节点的完整故事响应对象。
    :param db: 数据库会话
    :param story:  故事对象，包含故事的基本信息
    :return: CompleteStoryResponse: 包含完整故事树结构的响应对象，包括根节点和所有节点
    """
    # 查询故事的所有节点
    nodes: List[StoryNode] = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()

    # 将节点转换为响应对象并构建字典映射
    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=node.id,
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            options=node.options
        )
        node_dict[node.id] = node_response

    # 查找并验证根节点
    root_node = next((node for node in nodes if node.is_root), None)
    if not root_node:
        raise HTTPException(status_code=500, detail="Story root node not found")

    # 构建并返回完整的故事响应对象
    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[root_node.id],
        all_nodes=node_dict
    )

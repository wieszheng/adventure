# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/30 23:04
@Author   : wieszheng
@Software : PyCharm
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.job import StoryJob
from schemas.job import StoryJobResponse

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


@router.get("/{job_id}", response_model=StoryJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    获取指定工作ID的状态信息
    :param job_id: 工作的唯一标识符
    :param db: 数据库会话对象
    :return:
    """
    job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="找不到工作")

    return job

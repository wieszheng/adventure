# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/30 23:04
@Author   : wieszheng
@Software : PyCharm
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StoryJobBase(BaseModel):
    theme: str


class StoryJobResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    story_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StoryJobCreate(StoryJobBase):
    ...

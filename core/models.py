# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/30 23:02
@Author   : wieszheng
@Software : PyCharm
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StoryOptionLLM(BaseModel):
    """
    故事选项数据模型

    用于表示故事中每个节点的可选项，包含显示文本和下一个节点的信息
    """
    text: str = Field(description="向用户显示的选项的文本")
    nextNode: Dict[str, Any] = Field(description="下一个节点内容及其选项")


class StoryNodeLLM(BaseModel):
    """
    故事节点数据模型

    表示故事中的一个节点，包含节点内容、结束状态和可选项等信息
    """
    content: str = Field(description="故事节点的主要内容")
    isEnding: bool = Field(description="此节点是否为结束节点")
    isWinningEnding: bool = Field(description="该节点是否为获胜结束节点")
    options: Optional[List[StoryOptionLLM]] = Field(default=None, description="此节点的选项")


class StoryLLMResponse(BaseModel):
    """
    故事LLM响应数据模型

    用于表示完整故事的响应结构，包含标题和根节点信息
    """
    title: str = Field(description="故事的标题")
    rootNode: StoryNodeLLM = Field(description="故事的根节点")
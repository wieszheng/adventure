# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/30 23:03
@Author   : wieszheng
@Software : PyCharm
"""
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM
from dotenv import load_dotenv
import os

load_dotenv()


class StoryGenerator:
    """
    故事生成器类

    负责使用大语言模型生成互动式故事，并将生成的故事结构存储到数据库中。
    """
    @classmethod
    def _get_llm(cls):
        """
        获取大语言模型实例

        根据环境变量配置决定使用哪个LLM服务。优先使用阿里云DashScope服务，
        如果未配置则使用默认的OpenAI服务。
        :return: ChatOpenAI: 配置好的大语言模型实例
        """
        openai_api_key = os.getenv("OPENAI_API_KEY")
        service_url = os.getenv("BASE_URL")
        if openai_api_key and service_url:
            return ChatOpenAI(
                model="qwen-max",
                api_key=openai_api_key,
                base_url=service_url
            )

        return ChatOpenAI(model="qwen-max")

    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "幻想") -> Story:
        """
        生成完整的故事

        使用大语言模型根据指定主题生成一个完整的互动故事，并将其保存到数据库中。
        :param db: 数据库会话对象
        :param session_id: 用户会话ID
        :param theme: 故事主题
        :return: Story: 保存到数据库中的故事对象
        """
        # 获取大语言模型实例
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        # 构建故事生成提示模板
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                STORY_PROMPT
            ),
            (
                "human",
                f"以此主题创作故事: {theme}"
            )
        ]).partial(format_instructions=story_parser.get_format_instructions())

        # 调用大语言模型生成故事
        raw_response = llm.invoke(prompt.invoke({}))

        # 提取响应文本内容
        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        # 解析大语言模型的响应结果
        story_structure = story_parser.parse(response_text)

        # 创建故事记录并保存到数据库
        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()

        # 处理故事根节点数据
        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        # 递归处理故事节点
        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()
        return story_db

    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM,
                            is_root: bool = False) -> StoryNode:
        """
        处理故事节点数据，将其转换为数据库模型并保存

        :param db: 数据库会话对象
        :param story_id: 故事ID
        :param node_data: 故事节点数据，可以是StoryNodeLLM对象或字典
        :param is_root: 是否为根节点，默认为False
        :return: 保存到数据库的故事节点对象
        """
        # 创建故事节点对象，处理不同数据格式的兼容性
        node = StoryNode(
            story_id=story_id,
            content=node_data.content if hasattr(node_data, "content") else node_data["content"],
            is_root=is_root,
            is_ending=node_data.isEnding if hasattr(node_data, "isEnding") else node_data["isEnding"],
            is_winning_ending=node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data[
                "isWinningEnding"],
            options=[]
        )
        db.add(node)
        db.flush()

        # 如果不是结束节点且包含选项，则递归处理子节点
        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode

                # 如果下一个节点是字典格式，转换为StoryNodeLLM对象
                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)
                # 递归处理子节点
                child_node = cls._process_story_node(db, story_id, next_node, False)

                options_list.append({
                    "text": option_data.text,
                    "node_id": child_node.id
                })

            node.options = options_list

        db.flush()
        return node

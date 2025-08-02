# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/30 23:02
@Author   : wieszheng
@Software : PyCharm
"""
STORY_PROMPT = """
                您是一位富有创意的故事作家，可以创作引人入胜的选择自己的冒险故事。
                以我指定的 JSON 格式生成一个完整的分支故事，其中包含多个路径和结尾。

                这个故事应该有：
                1. 引人注目的标题
                2. 具有 2-3 个选项的起始情况（根节点）
                3. 每个选项都应指向另一个具有自己选项的节点
                4. 有些路径应该通向结局（赢和输）
                5. 至少一条路应该通向胜利的结局

                故事结构要求：
                - 每个节点应该有 2-3 个选项，结束节点除外
                - 故事应有 5-7 层深度（包括根节点）
                - 增加路径长度的多样性（有些结束得更早，有些结束得更晚）
                - 确保至少有一条获胜路径

                以此确切的 JSON 结构输出故事：
                {format_instructions}

                不要简化或省略故事结构的任何部分。
                不要在 JSON 结构之外添加任何文本。
                """

json_structure = """
        {
            "title": "故事标题",
            "rootNode": {
                "content": "故事的起始情况",
                "isEnding": false,
                "isWinningEnding": false,
                "options": [
                    {
                        "text": "选项 1 文本",
                        "nextNode": {
                            "content": "选项 1 会发生什么情况",
                            "isEnding": false,
                            "isWinningEnding": false,
                            "options": [
                                // 更多嵌套选项
                            ]
                        }
                    },
                    // 根节点的更多选项
                ]
            }
        }
        """

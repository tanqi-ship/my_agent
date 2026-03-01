"""
Agent模块：智能体核心逻辑
整合大模型、工具、RAG、对话记忆
"""

"""
显式声明 messages 的类型为 list[BaseMessage]，
因为所有消息类型（SystemMessage, HumanMessage, AIMessage, ToolMessage）都继承自 langchain_core.messages.BaseMessage
"""
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, ToolMessage
)
import config
from tools import get_all_tools
from rag import RAGSystem, search_documents, set_rag_instance
from typing import Any

class SmartAgent:
    """
    完整的智能Agent

    组成部分：
    1. 大模型（gemma3）- 大脑，负责理解和生成
    2. 工具集 - 手脚，负责执行具体操作
    3. RAG系统 - 知识库，提供文档信息
    4. 对话历史 - 记忆，保持上下文连贯
    """

    def __init__(self):
        """初始化Agent的所有组件"""

        # ===== 初始化RAG =====
        print("\n📚 初始化知识库...")
        self.rag = RAGSystem()
        set_rag_instance(self.rag)
        # 把RAG实例传给rag.py中的全局变量
        # 这样search_documents工具就能使用RAG了

        # ===== 收集所有工具 =====
        # 基础工具（时间、计算器、单位换算）+ RAG搜索工具
        self.tools = get_all_tools() + [search_documents]

        # 工具名 → 工具函数的映射
        self.tool_map = {t.name: t for t in self.tools}

        # ===== 初始化大模型 =====
        print("🤖 加载大模型...")
        self.llm = ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=config.OLLAMA_TEMPERATURE
        )
        # 绑定工具
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        print("  ✅ 大模型就绪")

        # ===== 对话历史 =====
        self.chat_history = []

        print("\n🎉 Agent初始化完成！")

    def chat(self, user_input: str) -> tuple[str, list[dict[str, Any]]]:
        """
        处理一轮对话，返回AI的回答

        参数：
            user_input: 用户输入的文字

        返回：
            AI的回答文字
        """

        # 构建消息列表
        messages = [SystemMessage(content=config.AGENT_SYSTEM_PROMPT)]
        messages: list[BaseMessage] = [SystemMessage(content=config.AGENT_SYSTEM_PROMPT)]
        messages.extend(self.chat_history[-config.MAX_HISTORY_MESSAGES:])
        messages.append(HumanMessage(content=user_input))

        # 用于记录本轮使用的工具（展示给用户看）
        tools_used = []

        # Agent推理循环
        for i in range(config.MAX_AGENT_ITERATIONS):

            response = self.llm_with_tools.invoke(messages)

            if hasattr(response, 'tool_calls') and response.tool_calls: # hasattr(response, 'tool_calls') 检查是否有 tool_calls
                # 模型决定调用工具
                messages.append(response)

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call.get("id", f"call_{i}")

                    # 执行工具
                    if tool_name in self.tool_map:
                        try:
                            result = self.tool_map[tool_name].invoke(tool_args)
                        except Exception as e:
                            result = f"工具执行出错：{str(e)}"
                    else:
                        result = f"未知工具：{tool_name}"

                    # 记录使用的工具
                    tools_used.append({
                        "name": tool_name,
                        "args": tool_args,
                        "result": str(result)[:200]
                    })

                    # 工具结果加入消息列表
                    messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id
                    ))
            else:
                # 不需要工具，直接回答
                final_answer = response.content if isinstance(response.content, str) else str(response.content) # 确保 response.content 是字符串
                break
        else:
            # for循环正常结束（没被break），说明达到最大次数
            # else在for循环中的用法：
            #   如果for循环正常结束（没有break），执行else
            #   如果for循环被break中断，不执行else
            final_answer = response.content or "抱歉，处理超时了。"

        # 更新对话历史
        self.chat_history.append(HumanMessage(content=user_input))
        self.chat_history.append(AIMessage(content=final_answer))

        return final_answer, tools_used
        # 返回两个值：回答 和 使用的工具列表
        # Python可以用逗号返回多个值，实际上返回的是一个元组(tuple)

    def clear_history(self):
        """清空对话历史"""
        self.chat_history.clear()

    def rebuild_knowledge_base(self):
        """重建知识库（文档更新后使用）"""
        self.rag.rebuild()

    def get_tool_names(self) -> list:
        """获取所有工具名称"""
        return [t.name for t in self.tools]
        # 列表推导式：等价于
        # names = []
        # for t in self.tools:
        #     names.append(t.name)
        # return names
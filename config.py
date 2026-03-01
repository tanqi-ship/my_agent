"""
配置文件：集中管理所有参数
好处：
  1. 修改参数不用翻代码，改这一个文件就行
  2. 不同环境（开发/生产）可以用不同配置
  3. 团队协作时，配置一目了然
"""
from text2vec import SentenceModel
import os

# ╔═══════════════════════════════════════════╗
# ║              模型配置                       ║
# ╚═══════════════════════════════════════════╝

# Ollama设置
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_TEMPERATURE = 0  # Agent决策用低温度，更稳定

# Embedding模型设置
EMBEDDING_MODEL_NAME = r"E:\MyPythonProject\my_agent\models\text2vec-base-chinese"
EMBEDDING_DEVICE = "cpu"  # Embedding模型用CPU，GPU留给大模型

# ╔═══════════════════════════════════════════╗
# ║              RAG配置                        ║
# ╚═══════════════════════════════════════════╝

# 文档路径
DOCS_PATH = os.path.join(os.path.dirname(__file__), "docs")
# os.path.dirname(__file__) 获取当前文件所在的目录
# os.path.join() 拼接路径，自动处理不同系统的路径分隔符
# Windows用 \，Mac/Linux用 /，join会自动处理

# 向量数据库路径
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "vector_db")

# 文本分割参数
CHUNK_SIZE = 300  # 每个块的最大字符数
CHUNK_OVERLAP = 50  # 相邻块的重叠字符数
SEPARATORS = ["\n\n", "\n", "。", "！", "？", "，", " ", ""]

# 检索参数
SEARCH_K = 3  # 每次检索返回的文档块数量
SEARCH_TYPE = "similarity"  # 搜索类型

# ╔═══════════════════════════════════════════╗
# ║              Agent配置                      ║
# ╚═══════════════════════════════════════════╝

# Agent最大推理循环次数
MAX_AGENT_ITERATIONS = 5

# 对话历史最大保留轮数（1轮 = 1条human + 1条ai = 2条消息）
MAX_HISTORY_ROUNDS = 8
MAX_HISTORY_MESSAGES = MAX_HISTORY_ROUNDS * 2  # 16条消息

# Agent系统提示词
AGENT_SYSTEM_PROMPT = """你是一个全能的智能助手，名叫"小智"。

你拥有以下工具：
1. search_documents - 搜索本地知识库（公司制度、产品手册等文档）
2. get_current_time - 查询当前时间日期
3. calculator - 数学计算
4. unit_converter - 单位换算

工作原则：
1. 根据用户问题，自主判断是否需要使用工具
2. 涉及公司规定、产品使用等问题，务必先用search_documents搜索文档
3. 需要计算时，使用calculator确保准确
4. 普通闲聊直接回答，不需要工具
5. 所有回答使用中文，简洁准确
6. 如果不确定，诚实地说不知道
7. 适当标注信息来源
8. **最终回答必须是自然语言，不要输出 JSON、代码或工具调用指令。**"""

# ╔═══════════════════════════════════════════╗
# ║              Web界面配置                    ║
# ╚════════════════════════════════════════ ═══╝

WEB_HOST = "0.0.0.0"  # 监听所有网卡，局域网内其他设备也能访问
WEB_PORT = 7860  # 端口号
WEB_TITLE = "🤖 小智 - 全能AI助手"
WEB_DESCRIPTION = """
### 功能介绍
- 📚 **文档问答**：基于本地知识库回答问题
- 🔢 **数学计算**：精确的数学运算
- 📏 **单位换算**：温度、长度、重量换算
- ⏰ **时间查询**：当前日期时间
- 💬 **智能对话**：记住上下文的连续对话
"""

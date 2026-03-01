"""
RAG模块：文档加载、向量化、检索
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# ============ 【修改 1/4】导入部分 ============
# 原 Chroma 导入（注释掉）
# from langchain_chroma import Chroma

# 新增 FAISS 导入
from langchain_community.vectorstores import FAISS  # 👈 新增

from langchain_core.tools import tool
import os
import config


class RAGSystem:
    """
    RAG系统类
    负责文档的加载、向量化、存储和检索
    """

    def __init__(self):
        """初始化RAG系统"""
        self.embedding_model = None
        self.vector_db = None
        self._init_embedding()
        self._init_vector_db()

    def _init_embedding(self):
        print("🧮 加载Embedding模型...")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL_NAME,
            model_kwargs={"device": config.EMBEDDING_DEVICE},
            encode_kwargs={"normalize_embeddings": True}
        )
        print("  ✅ Embedding模型就绪")

    # ============ 【修改 2/4】初始化向量数据库 ============
    def _init_vector_db(self):
        """初始化向量数据库"""
        db_path = config.VECTOR_DB_PATH
        index_file = os.path.join(db_path, "index.faiss")  # 👈 FAISS 的索引文件

        if os.path.exists(index_file):  # 👈 检查 index.faiss 是否存在
            print("💾 加载已有向量数据库...")
            self.vector_db = FAISS.load_local(
                db_path,
                self.embedding_model,
                allow_dangerous_deserialization=True  # 👈 FAISS 必须加
            )
        else:
            print("🆕 创建向量数据库...")
            self._build_vector_db()

        count = len(self.vector_db.index_to_docstore_id)  # 👈 FAISS 获取数量的方式
        print(f"  ✅ 向量数据库就绪，共 {count} 个文本块")

    # ============ 【修改 3/4】构建向量数据库 ============
    def _build_vector_db(self):
        """构建向量数据库"""
        loader = DirectoryLoader(
            path=config.DOCS_PATH,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()
        print(f"  📄 加载了 {len(documents)} 个文档")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=config.SEPARATORS
        )
        chunks = splitter.split_documents(documents)
        print(f"  ✂️ 分割成 {len(chunks)} 个文本块")

        # 使用 FAISS 构建
        self.vector_db = FAISS.from_documents(
            documents=chunks,
            embedding=self.embedding_model
        )
        # 保存到磁盘
        self.vector_db.save_local(config.VECTOR_DB_PATH)  # 👈 保存方法

    def search(self, query: str, k: int = None) -> str:
        """搜索相关文档（无需修改，FAISS 接口兼容）"""
        if k is None:
            k = config.SEARCH_K

        results = self.vector_db.similarity_search_with_score(query, k=k)

        if not results:
            return "未找到相关文档"

        output_parts = []
        for i, (doc, score) in enumerate(results):
            source = os.path.basename(doc.metadata.get("source", "未知"))
            relevance = max(0, 1 - score)
            output_parts.append(
                f"[资料{i + 1} | 来源:{source} | 相关度:{relevance:.2f}]\n"
                f"{doc.page_content}"
            )

        return "\n\n".join(output_parts)

    # ============ 【修改 4/4】重建向量数据库 ============
    def rebuild(self):
        """
        重建向量数据库
        """
        import shutil

        db_path = config.VECTOR_DB_PATH
        if os.path.exists(db_path):
            shutil.rmtree(db_path)  # 👈 FAISS 无文件锁，直接删！
            print("🗑️ 已删除旧的向量数据库")

        self._build_vector_db()
        print("✅ 向量数据库重建完成！")


# ============ RAG搜索工具（给Agent用） ============
_rag_instance = None

def set_rag_instance(rag: RAGSystem):
    global _rag_instance
    _rag_instance = rag

@tool(description="搜索本地知识库文档。当用户询问公司制度、产品使用方法、报销规定、考勤规则等与公司或产品相关的问题时，使用此工具搜索文档。输入为搜索关键词或问题。")
def search_documents(query: str) -> str:
    global _rag_instance
    if _rag_instance is None:
        return "文档系统未初始化"
    return _rag_instance.search(query)
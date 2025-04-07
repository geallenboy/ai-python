import streamlit as st
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.qdrant import Qdrant
from agno.models.ollama import Ollama
from agno.embedder.ollama import OllamaEmbedder
import tempfile
import os

def init_session_state():
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = None
    if 'legal_team' not in st.session_state:
        st.session_state.legal_team = None
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None

def init_qdrant():
    """初始化本地 Qdrant 向量数据库"""
    return Qdrant(
        collection="legal_knowledge",
        url="http://localhost:6333", 
        embedder=OllamaEmbedder(model="openhermes")
    )

def process_document(uploaded_file, vector_db: Qdrant):
    """处理上传的文档"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            st.write("📄 正在处理文档...")
            knowledge_base = PDFKnowledgeBase(
                path=temp_dir,
                vector_db=vector_db,
                reader=PDFReader(chunk=True),
                recreate_vector_db=True
            )
            
            st.write("📚 正在加载知识库...")
            knowledge_base.load()

            st.write("✅ 正在验证知识库...")
            test_results = knowledge_base.search("test")
            if not test_results:
                raise Exception("知识库验证失败")
            
            st.write("📦 知识库已就绪！")
            return knowledge_base
            
        except Exception as e:
            raise Exception(f"文档处理出错：{str(e)}")

def main():
    st.set_page_config(page_title="本地法律文档分析助手", layout="wide")
    init_session_state()

    st.title("⚖️ 本地 AI 法律代理团队")

    if not st.session_state.vector_db:
        try:
            st.session_state.vector_db = init_qdrant()
            st.success("✅ 已连接到本地 Qdrant 数据库！")
        except Exception as e:
            st.error(f"❌ 无法连接到 Qdrant：{str(e)}")
            return

    st.header("📤 上传法律文档")
    uploaded_file = st.file_uploader("请上传 PDF 格式的法律文档", type=['pdf'])
    
    if uploaded_file:
        with st.spinner("正在处理文档..."):
            try:
                knowledge_base = process_document(uploaded_file, st.session_state.vector_db)
                st.session_state.knowledge_base = knowledge_base
                
                legal_researcher = Agent(
                    name="法律研究员",
                    role="擅长法律研究和判例分析",
                    model=Ollama(id="llama3.1:8b"),  
                    knowledge=st.session_state.knowledge_base,
                    search_knowledge=True,
                    instructions=[
                        "查找并引用相关法律案例与先例",
                        "提供带来源的详细研究摘要",
                        "引用上传文档的具体段落"
                    ],
                    markdown=True
                )

                contract_analyst = Agent(
                    name="合同分析师",
                    role="专注于合同条款审查和问题识别",
                    model=Ollama(id="llama3.1:8b"),
                    knowledge=knowledge_base,
                    search_knowledge=True,
                    instructions=[
                        "全面审查合同内容",
                        "识别关键条款和潜在问题",
                        "引用文档中具体条款"
                    ],
                    markdown=True
                )

                legal_strategist = Agent(
                    name="法律战略师", 
                    role="擅长制定法律应对策略",
                    model=Ollama(id="llama3.1:8b"),
                    knowledge=knowledge_base,
                    search_knowledge=True,
                    instructions=[
                        "制定全面的法律策略",
                        "提供可执行的建议",
                        "综合考虑风险与机会"
                    ],
                    markdown=True
                )

                st.session_state.legal_team = Agent(
                    name="团队负责人",
                    role="协调整个法律团队的工作",
                    model=Ollama(id="llama3.1:8b"),
                    team=[legal_researcher, contract_analyst, legal_strategist],
                    knowledge=st.session_state.knowledge_base,
                    search_knowledge=True,
                    instructions=[
                        "协调各代理之间的分析",
                        "提供全面且有来源的分析结果",
                        "引用文档中具体内容"
                    ],
                    markdown=True
                )
                
                st.success("📄 文档处理完成，法律团队已初始化！")
                    
            except Exception as e:
                st.error(f"❌ 文档处理出错：{str(e)}")

        st.divider()
        st.header("🔍 分析选项")
        analysis_type = st.selectbox(
            "请选择分析类型",
            [
                "合同审查",
                "法律研究",
                "风险评估",
                "合规检查",
                "自定义问题"
            ]
        )

    if not st.session_state.vector_db:
        st.info("👈 正在连接 Qdrant 向量数据库...")
    elif not uploaded_file:
        st.info("👈 请上传法律文档以开始分析")
    elif st.session_state.legal_team:
        st.header("📊 文档分析")
  
        analysis_configs = {
            "合同审查": {
                "query": "请审查此合同并识别关键条款、义务和潜在问题。",
                "agents": ["合同分析师"],
                "description": "详细分析合同内容，关注条款和义务"
            },
            "法律研究": {
                "query": "请研究与本合同相关的判例与法律条文。",
                "agents": ["法律研究员"],
                "description": "寻找相关法律案例与先例"
            },
            "风险评估": {
                "query": "请分析此文档中的法律风险与潜在责任。",
                "agents": ["合同分析师", "法律战略师"],
                "description": "联合分析潜在风险与法律影响"
            },
            "合规检查": {
                "query": "请检查该文件中是否存在监管合规问题。",
                "agents": ["法律研究员", "合同分析师", "法律战略师"],
                "description": "综合检查法律合规性"
            },
            "自定义问题": {
                "query": None,
                "agents": ["法律研究员", "合同分析师", "法律战略师"],
                "description": "使用全部代理回答你的具体问题"
            }
        }

        st.info(f"📋 分析说明：{analysis_configs[analysis_type]['description']}")
        st.write(f"🧠 启动代理：{', '.join(analysis_configs[analysis_type]['agents'])}")

        user_query = st.text_area(
            "请输入你的问题或关注点：",
            help="可以输入具体问题或你想要关注的内容"
        )

        if st.button("开始分析"):
            if user_query or analysis_type != "自定义问题":
                with st.spinner("正在分析文档..."):
                    try:
                        if analysis_type != "自定义问题":
                            combined_query = f"""
                            请以上传文档为参考：

                            主要分析任务：{analysis_configs[analysis_type]['query']}
                            补充问题：{user_query if user_query else '无'}

                            分析参与代理：{', '.join(analysis_configs[analysis_type]['agents'])}

                            请引用知识库内容并标明文档中出处。
                            """
                        else:
                            combined_query = user_query

                        response = st.session_state.legal_team.run(combined_query)
                        
                        tabs = st.tabs(["📖 分析详情", "📌 关键要点", "✅ 建议"])

                        with tabs[0]:
                            st.markdown("### 📖 分析详情")
                            if response.content:
                                st.markdown(response.content)
                            else:
                                for message in response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)

                        with tabs[1]:
                            st.markdown("### 📌 关键要点")
                            key_points_response = st.session_state.legal_team.run(
                                f"""请根据以下分析内容：
                                {response.content}

                                总结分析要点（以项目符号形式展示），
                                着重体现以下代理的见解：{', '.join(analysis_configs[analysis_type]['agents'])}"""
                            )
                            if key_points_response.content:
                                st.markdown(key_points_response.content)
                            else:
                                for message in key_points_response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)

                        with tabs[2]:
                            st.markdown("### ✅ 建议与行动方案")
                            recommendations_response = st.session_state.legal_team.run(
                                f"""请根据以下分析内容：
                                {response.content}

                                给出主要建议和最佳行动方案，
                                请具体说明以下代理的建议：{', '.join(analysis_configs[analysis_type]['agents'])}"""
                            )
                            if recommendations_response.content:
                                st.markdown(recommendations_response.content)
                            else:
                                for message in recommendations_response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)

                    except Exception as e:
                        st.error(f"❌ 分析出错：{str(e)}")
            else:
                st.warning("⚠️ 请输入分析问题或选择分析类型")
    else:
        st.info("请上传法律文档以开始分析")

if __name__ == "__main__":
    main()

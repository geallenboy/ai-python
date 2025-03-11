import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.models.deepseek import DeepSeek
import os
import pyperclip
from streamlit_javascript import st_javascript
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="AI健康与健身规划师",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0fff4;
        border: 1px solid #9ae6b4;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fffaf0;
        border: 1px solid #fbd38d;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .copy-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.25rem 0.75rem;
        background-color: #f1f3f4;
        border: 1px solid #dadce0;
        border-radius: 4px;
        color: #3c4043;
        font-size: 0.85rem;
        cursor: pointer;
        margin-left: 0.5rem;
    }
    .copy-btn:hover {
        background-color: #e8eaed;
    }
    .content-container {
        position: relative;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 复制功能的JavaScript
copy_js = """
function copyToClipboard(text) {
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    return true;
}
"""

def add_copy_button(text, key):
    col1, col2 = st.columns([0.95, 0.05])
    with col1:
        st.markdown(f"""
        <div class="content-container">
            {text}
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("📋", key=f"copy_{key}", help="复制内容"):
            # 先处理文本，将反斜杠和反引号进行转义
            escaped_text = text.replace("\\", "\\\\").replace("`", "\\`")
            js_code = f"{copy_js}; copyToClipboard(`{escaped_text}`);"
            success = st_javascript(js_code)
            if success:
                st.success("已复制到剪贴板！", icon="✅")

def display_dietary_plan(plan_content):
    with st.expander("📋 您的个性化饮食计划", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 为什么这个计划有效")
            st.info(plan_content.get("why_this_plan_works", "信息不可用"))
            
            st.markdown("### 🍽️ 膳食计划")
            add_copy_button(plan_content.get("meal_plan", "计划不可用"), "meal_plan")
        
        with col2:
            st.markdown("### ⚠️ 重要注意事项")
            considerations = plan_content.get("important_considerations", "").split('\n')
            for consideration in considerations:
                if consideration.strip():
                    st.warning(consideration)

def display_fitness_plan(plan_content):
    with st.expander("💪 您的个性化健身计划", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 目标")
            st.success(plan_content.get("goals", "未指定目标"))
            
            st.markdown("### 🏋️‍♂️ 锻炼方案")
            add_copy_button(plan_content.get("routine", "方案不可用"), "fitness_routine")
        
        with col2:
            st.markdown("### 💡 专业提示")
            tips = plan_content.get("tips", "").split('\n')
            for tip in tips:
                if tip.strip():
                    st.info(tip)

def initialize_model(provider, api_key, model_name):
    """初始化选定的模型"""
    if provider == "OpenAI":
        return OpenAIChat(id=model_name, api_key=api_key)
    elif provider == "Google":
        return Gemini(id=model_name, api_key=api_key)
    elif provider == "Deepseek":
        return DeepSeek(id=model_name, api_key=api_key)
    else:
        raise ValueError(f"不支持的提供商: {provider}")

def main():
   

    if 'dietary_plan' not in st.session_state:
        st.session_state.dietary_plan = {}
        st.session_state.fitness_plan = {}
        st.session_state.qa_pairs = []
        st.session_state.plans_generated = False

    st.title("🏋️‍♂️ AI健康与健身规划师")
    st.markdown("""
        <div style='padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; background-color: #f8f9fa;'>
        获取根据您的目标和偏好量身定制的饮食和健身计划。
        我们的AI驱动系统考虑您的独特情况，为您创建完美的计划。
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔑 API配置")
        
        # 模型提供商选择
        provider = st.selectbox(
            "选择AI提供商",
            options=["OpenAI", "Google", "Deepseek"],
            index=0,
            help="选择AI模型提供商"
        )
        
        # 根据提供商提供不同的模型选项
        if provider == "OpenAI":
            model_options = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            api_key_help = "输入您的OpenAI API密钥"
            api_key_link = "[在此处获取您的API密钥](https://platform.openai.com/api-keys)"
        elif provider == "Google":
            model_options = ["gemini-1.5-pro", "gemini-1.5-flash"]
            api_key_help = "输入您的Google AI Studio API密钥"
            api_key_link = "[在此处获取您的API密钥](https://aistudio.google.com/)"
        elif provider == "Deepseek":
            model_options = ["deepseek-chat", "deepseek-coder"]
            api_key_help = "输入您的Deepseek API密钥"
            api_key_link = "[在此处获取您的API密钥](https://platform.deepseek.com/)"
        
        api_key = st.text_input(
            f"{provider} API密钥",
            type="password",
             value=openai_api_key,
            help=api_key_help
        )
        
        # 模型选择
        model_choice = st.selectbox(
            "选择模型",
            options=model_options,
            index=0,
            help=f"选择要使用的{provider}模型"
        )
        
        # 流式输出选项
        use_streaming = st.checkbox("启用流式输出", value=True, help="启用后，AI响应将实时流式显示")
        
        if not api_key:
            st.warning(f"⚠️ 请输入您的{provider} API密钥以继续")
            st.markdown(api_key_link)
            return
        
        st.success("API密钥已接受！")

    if api_key:
        try:
            # 初始化选定的模型
            selected_model = initialize_model(provider, api_key, model_choice)
            
            Agent(model=selected_model)
         
        except Exception as e:
            st.error(f"❌ 初始化{provider}模型或验证API密钥时出错: {e}")
            st.warning(f"请确保您安装了兼容的agno和{provider.lower()}包版本。推荐：agno>=0.4.0")
            return

        st.header("👤 您的个人资料")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("年龄", min_value=10, max_value=100, step=1, help="输入您的年龄")
            height = st.number_input("身高 (厘米)", min_value=100.0, max_value=250.0, step=0.1)
            activity_level = st.selectbox(
                "活动水平",
                options=["久坐不动", "轻度活动", "中度活动", "高度活动", "极度活动"],
                help="选择您的典型活动水平"
            )
            dietary_preferences = st.selectbox(
                "饮食偏好",
                options=["无特殊偏好","肉食", "素食", "生酮饮食", "无麸质", "低碳水", "无乳制品"],
                help="选择您的饮食偏好"
            )

        with col2:
            weight = st.number_input("体重 (公斤)", min_value=20.0, max_value=300.0, step=0.1)
            sex = st.selectbox("性别", options=["男", "女", "其他"])
            fitness_goals = st.selectbox(
                "健身目标",
                options=["减肥", "增肌", "耐力", "保持健康", "力量训练"],
                help="您想要达到什么目标？"
            )

        # 当用户点击"生成我的个性化计划"按钮时
        if st.button("🎯 生成我的个性化计划", use_container_width=True):
            with st.spinner("正在为您创建完美的健康和健身方案..."):
                try:
                    # 初始化模型
                    selected_model = initialize_model(provider, api_key, model_choice)
                    
                    # 创建饮食专家代理
                    dietary_agent = Agent(
                        name="饮食专家",
                        role="提供个性化饮食建议",
                        model=selected_model,
                        instructions=[
                            "考虑用户的输入，包括饮食限制和偏好。",
                            "建议一天的详细膳食计划，包括早餐、午餐、晚餐和零食。",
                            "简要解释为什么该计划适合用户的目标。",
                            "注重建议的清晰度、连贯性和质量。",
                        ],
                        markdown=True  # 添加这个参数
                    )

                    # 创建健身专家代理
                    fitness_agent = Agent(
                        name="健身专家",
                        role="提供个性化健身建议",
                        model=selected_model,
                        instructions=[
                            "提供针对用户目标的运动。",
                            "包括热身、主要锻炼和放松运动。",
                            "解释每个推荐运动的好处。",
                            "确保计划可行且详细。",
                        ],
                        markdown=True  # 添加这个参数
                    )

                    user_profile = f"""
                    年龄: {age}
                    体重: {weight}kg
                    身高: {height}cm
                    性别: {sex}
                    活动水平: {activity_level}
                    饮食偏好: {dietary_preferences}
                    健身目标: {fitness_goals}
                    """

                    # 饮食计划流式输出（修改后）
                    if use_streaming:
                        dietary_placeholder = st.empty()
                        dietary_content = ""
                        
                        try:
                            # 注意这里的改动，确保run方法被正确调用
                            run_response = dietary_agent.run(user_profile, stream=True)
                            
                            # 检查返回的是否是有效迭代器
                            if run_response:
                                for chunk in run_response:
                                    if hasattr(chunk, 'content') and chunk.content:
                                        dietary_content += chunk.content
                                        dietary_placeholder.markdown(dietary_content + "▌")
                                
                                # 最后一次更新，不带光标
                                dietary_placeholder.markdown(dietary_content)
                                dietary_plan_response = dietary_content
                            else:
                                st.error("无法获取响应流")
                                dietary_plan_response = "无法生成饮食计划。请检查API设置并重试。"
                        except Exception as e:
                            st.error(f"处理饮食计划流时出错: {e}")
                            dietary_plan_response = "处理错误。请检查API设置并重试。"
                    else:
                        # 非流式输出
                        try:
                            response = dietary_agent.run(user_profile)
                            if hasattr(response, 'content'):
                                dietary_plan_response = response.content
                            else:
                                dietary_plan_response = str(response)
                        except Exception as e:
                            st.error(f"获取饮食计划时出错: {e}")
                            dietary_plan_response = "无法生成饮食计划。请检查API设置并重试。"

                    # 构建饮食计划对象
                    dietary_plan = {
                        "why_this_plan_works": "高蛋白、健康脂肪、适量碳水化合物和热量平衡",
                        "meal_plan": dietary_plan_response,
                        "important_considerations": """
                        - 水分摄入：全天多喝水
                        - 电解质：监控钠、钾和镁水平
                        - 纤维：通过蔬菜和水果确保充足摄入
                        - 倾听身体需求：根据需要调整份量
                        """
                    }

                    # 健身计划流式输出（修改后）
                    if use_streaming:
                        fitness_placeholder = st.empty()
                        fitness_content = ""
                        
                        try:
                            # 注意这里的改动，确保run方法被正确调用
                            run_response = fitness_agent.run(user_profile, stream=True)
                            
                            # 检查返回的是否是有效迭代器
                            if run_response:
                                for chunk in run_response:
                                    if hasattr(chunk, 'content') and chunk.content:
                                        fitness_content += chunk.content
                                        fitness_placeholder.markdown(fitness_content + "▌")
                                
                                # 最后一次更新，不带光标
                                fitness_placeholder.markdown(fitness_content)
                                fitness_plan_response = fitness_content
                            else:
                                st.error("无法获取响应流")
                                fitness_plan_response = "无法生成健身计划。请检查API设置并重试。"
                        except Exception as e:
                            st.error(f"处理健身计划流时出错: {e}")
                            fitness_plan_response = "处理错误。请检查API设置并重试。"
                    else:
                        # 非流式输出
                        try:
                            response = fitness_agent.run(user_profile)
                            if hasattr(response, 'content'):
                                fitness_plan_response = response.content
                            else:
                                fitness_plan_response = str(response)
                        except Exception as e:
                            st.error(f"获取健身计划时出错: {e}")
                            fitness_plan_response = "无法生成健身计划。请检查API设置并重试。"

                    # 构建健身计划对象
                    fitness_plan = {
                        "goals": "增强力量，提高耐力，保持整体健康",
                        "routine": fitness_plan_response,
                        "tips": """
                        - 定期跟踪您的进度
                        - 锻炼之间允许适当休息
                        - 专注于正确的姿势
                        - 保持锻炼的一致性
                        """
                    }

                    # 更新会话状态
                    st.session_state.dietary_plan = dietary_plan
                    st.session_state.fitness_plan = fitness_plan
                    st.session_state.plans_generated = True
                    st.session_state.qa_pairs = []

                    # 显示计划
                    display_dietary_plan(dietary_plan)
                    display_fitness_plan(fitness_plan)

                except Exception as e:
                    st.error(f"❌ 发生错误: {e}")
                    st.info(f"如果错误与{provider} API或agno有关，请确保您已安装兼容的版本。推荐：agno>=0.4.0")

        if st.session_state.plans_generated:
            st.header("❓ 关于您计划的问题？")
            question_input = st.text_input("您想了解什么？")

            # 处理用户问题
            if st.button("获取回答"):
                if question_input:
                    with st.spinner("为您寻找最佳答案..."):
                        dietary_plan = st.session_state.dietary_plan
                        fitness_plan = st.session_state.fitness_plan

                        context = f"饮食计划: {dietary_plan.get('meal_plan', '')}\n\n健身计划: {fitness_plan.get('routine', '')}"
                        full_context = f"{context}\n用户问题: {question_input}"

                        try:
                            # 初始化问答代理
                            qa_agent = Agent(
                                name="健康顾问",
                                role="回答有关健康和健身计划的问题",
                                model=selected_model,
                                instructions=[
                                    "根据提供的饮食和健身计划回答用户问题",
                                    "提供清晰、准确、有帮助的回答",
                                    "如果用户问题超出计划范围，建议他们咨询专业人士"
                                ],
                                markdown=True
                            )
                            
                            # 流式输出Q&A答案（修改后）
                            if use_streaming:
                                qa_placeholder = st.empty()
                                qa_content = ""
                                
                                try:
                                    # 明确指定stream参数
                                    run_response = qa_agent.run(full_context, stream=True)
                                    
                                    if run_response:
                                        for chunk in run_response:
                                            if hasattr(chunk, 'content') and chunk.content:
                                                qa_content += chunk.content
                                                qa_placeholder.markdown(qa_content + "▌")
                                        
                                        # 最后一次更新，不带光标
                                        qa_placeholder.markdown(qa_content)
                                        answer = qa_content
                                    else:
                                        st.error("无法获取响应流")
                                        answer = "抱歉，我现在无法回答您的问题。请稍后再试。"
                                except Exception as e:
                                    st.error(f"处理回答流时出错: {e}")
                                    answer = f"处理错误: {str(e)}"
                            else:
                                # 非流式输出
                                try:
                                    run_response = qa_agent.run(full_context)
                                    if hasattr(run_response, 'content'):
                                        answer = run_response.content
                                    else:
                                        answer = str(run_response)
                                except Exception as e:
                                    st.error(f"获取回答时出错: {e}")
                                    answer = "抱歉，我现在无法生成回应。"

                            # 添加到问答历史
                            st.session_state.qa_pairs.append((question_input, answer))
                        except Exception as e:
                            st.error(f"❌ 获取答案时发生错误: {e}")

            if st.session_state.qa_pairs:
                st.header("💬 问答历史")
                for i, (question, answer) in enumerate(st.session_state.qa_pairs):
                    st.markdown(f"**问:** {question}")
                    add_copy_button(answer, f"qa_answer_{i}")

if __name__ == "__main__":
    main()
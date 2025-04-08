import os
from PIL import Image as PILImage
from agno.agent import Agent
from agno.models.google import Gemini
import streamlit as st
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.media import Image as AgnoImage

# API 密钥状态初始化
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = None

# 侧边栏设置
with st.sidebar:
    st.title("ℹ️ 配置")

    if not st.session_state.GOOGLE_API_KEY:
        api_key = st.text_input(
            "请输入您的 Google API 密钥：",
            type="password"
        )
        st.caption(
            "您可以从 [Google AI Studio](https://aistudio.google.com/apikey) 获取您的 API 密钥 🔑"
        )
        if api_key:
            st.session_state.GOOGLE_API_KEY = api_key
            st.success("API 密钥已保存！")
            st.rerun()
    else:
        st.success("API 密钥已配置")
        if st.button("🔄 重置 API 密钥"):
            st.session_state.GOOGLE_API_KEY = None
            st.rerun()

    st.info(
        "该工具使用先进的计算机视觉技术和放射学专业知识，提供医学影像数据的 AI 辅助分析。"
    )
    st.warning(
        "⚠免责声明：本工具仅供教育和信息参考使用，所有分析结果应由专业医疗人员进行审阅。"
        "请勿仅依赖本工具进行医疗决策。"
    )

# 创建医学影像 AI 代理
medical_agent = Agent(
    model=Gemini(
        id="gemini-2.0-flash",
        api_key=st.session_state.GOOGLE_API_KEY
    ),
    tools=[DuckDuckGoTools()],
    markdown=True
) if st.session_state.GOOGLE_API_KEY else None

if not medical_agent:
    st.warning("请在侧边栏中配置 API 密钥以继续使用")

# 医学分析查询提示词
query = """
你是一位经验丰富的医学影像专家，具有深厚的放射学与诊断影像知识。请分析患者上传的医学影像，并按照以下结构组织你的分析：

### 1. 图像类型与区域
- 指明成像类型（X 光 / MRI / CT / 超声等）
- 确定图像所展示的人体解剖区域与拍摄角度
- 评价图像质量与技术适当性

### 2. 主要发现
- 系统性地列出主要观察结果
- 明确指出影像中的任何异常，并进行精确描述
- 如适用，提供尺寸、密度等测量数据
- 描述病灶位置、大小、形状和特征
- 严重程度评级：正常 / 轻度 / 中度 / 重度

### 3. 诊断评估
- 给出主要诊断及其置信度
- 按可能性列出鉴别诊断
- 每个诊断需结合影像中的依据进行说明
- 指出任何紧急或严重的发现

### 4. 面向患者的解释
- 用简单明了的语言解释上述发现，便于患者理解
- 避免使用专业术语，或提供清晰定义
- 如有帮助，可使用形象类比
- 回应患者可能关心的问题

### 5. 研究参考
重要：请使用 DuckDuckGo 搜索工具进行以下研究：
- 查找类似病例的最新医学文献
- 搜索标准治疗方案
- 提供相关医学参考链接列表
- 查找相关技术进展
- 引用 2-3 个关键文献作为支持

请使用清晰的 Markdown 标题和项目符号格式，内容简洁但详尽。
"""

# 主页面标题
st.title("🏥 医学影像诊断智能助手")
st.write("请上传一张医学影像图，我们将为您提供专业的 AI 辅助分析")

# 页面结构容器
upload_container = st.container()
image_container = st.container()
analysis_container = st.container()

# 上传图像部分
with upload_container:
    uploaded_file = st.file_uploader(
        "上传医学影像",
        type=["jpg", "jpeg", "png", "dicom"],
        help="支持的格式：JPG、JPEG、PNG、DICOM"
    )

# 图像展示与分析按钮
if uploaded_file is not None:
    with image_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image = PILImage.open(uploaded_file)
            width, height = image.size
            aspect_ratio = width / height
            new_width = 500
            new_height = int(new_width / aspect_ratio)
            resized_image = image.resize((new_width, new_height))
            
            st.image(
                resized_image,
                caption="上传的医学影像",
                use_container_width=True
            )
            
            analyze_button = st.button(
                "🔍 开始分析",
                type="primary",
                use_container_width=True
            )
    
    # 分析结果展示区域
    with analysis_container:
        if analyze_button:
            with st.spinner("🔄 正在分析图像，请稍候..."):
                try:
                    temp_path = "temp_resized_image.png"
                    resized_image.save(temp_path)
                    
                    # 创建 Agno 图像对象
                    agno_image = AgnoImage(filepath=temp_path)
                    
                    # 运行 AI 分析
                    response = medical_agent.run(query, images=[agno_image])
                    
                    st.markdown("### 📋 分析结果")
                    st.markdown("---")
                    st.markdown(response.content)
                    st.markdown("---")
                    st.caption(
                        "提示：此分析由 AI 生成，仅供参考。请由专业医生进行复核。"
                    )
                except Exception as e:
                    st.error(f"分析出错：{e}")
else:
    st.info("👆 请上传医学图像以开始分析")

from typing import Dict, List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
firecarawl_api_key = os.getenv("FIRECRAWl_API_KEY")
class PropertyData(BaseModel):
    """房产数据提取的结构"""
    building_name: str = Field(description="房产名称", alias="Building_name")
    property_type: str = Field(description="房产类型（商业、住宅等））", alias="Property_type")
    location_address: str = Field(description="地址")
    price: str = Field(description="房产价格（元）", alias="Price")
    description: str = Field(description="房产详细描述", alias="Description")

class PropertiesResponse(BaseModel):
    """多个房产响应的结构"""
    properties: List[PropertyData] = Field(description="房产详情列表")

class LocationData(BaseModel):
    """地点价格趋势的结构"""
    location: str
    price_per_sqm: float = Field(description="每平米价格（元）")
    percent_increase: float
    rental_yield: float

class LocationsResponse(BaseModel):
    """多个地点响应的结构"""
    locations: List[LocationData] = Field(description="地点数据点列表")

class FirecrawlResponse(BaseModel):
    """Firecrawl API响应的结构"""
    success: bool
    data: Dict
    status: str
    expiresAt: str

class PropertyFindingAgent:
    """负责寻找房产并提供推荐的代理人"""
    
    def __init__(self, firecrawl_api_key: str, openai_api_key: str, model_id: str = "gpt-4o"):
        self.agent = Agent(
            model=OpenAIChat(id=model_id, api_key=openai_api_key),
            markdown=True,
            description="我是一名房地产专家，帮助根据用户偏好寻找和分析房产。"
        )
        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

    def find_properties(
        self, 
        city: str,
        max_price: float,
        property_category: str = "住宅",
        property_type: str = "住宅"
    ) -> str:
        """根据用户偏好寻找和分析房产"""
        formatted_location = city.lower()
        print("formatted_location:", formatted_location)
        urls = [
            # f"https://beijing.anjuke.com/sale/",
            f"https://bj.ke.com/ershoufang/",
            # f"https://bj.fang.com/",
            # f"https://bj.58.com/ershoufang/"
        ]
        
        print("urls:", urls,property_type)
        # property_type_prompt = "住宅"
        print("city:", city)
        print("max_price:", max_price)
        print("property_category:", property_category)
        raw_response = self.firecrawl.extract(
            urls=urls,
            params={
                'prompt': f"""仅提取{city}中价格低于{max_price}万元的10个或更少的不同{property_category} {property_type}。
                
                要求：
                - 房产类别：仅{property_category}房产
                - 房产类型：仅{property_type}
                - 位置：{city}
                - 最高价格：{max_price}万元
                - 包含完整的房产详情和确切位置
                - 重要：至少返回3个不同房产的数据。最多10个。
                - 格式为带有各自详情的房产列表
                """,
                'schema': PropertiesResponse.model_json_schema()
            }
        )
        
        print("原始房产响应：", raw_response)
        
        if isinstance(raw_response, dict) and raw_response.get('success'):
            properties = raw_response['data'].get('properties', [])
        else:
            properties = []
            
        print("处理后的房产：", properties)

        
        analysis = self.agent.run(
            f"""作为房地产专家，分析这些房产和市场趋势：

            以json格式找到的房产：
            {properties}

            **重要说明：**
            1. 仅分析符合用户要求的上述JSON数据中的房产：
               - 房产类别：{property_category}
               - 房产类型：{property_type}
               - 最高价格：{max_price}万元
            2. 不要创建新的类别或房产类型
            3. 从匹配的房产中，选择价格最接近{max_price}万元的5-6个房产

            请按以下格式提供您的分析：
            
            🏠 精选房产
            • 仅列出价格最接近{max_price}万元的5-6个最佳匹配房产
            • 对于每个房产包括：
              - 名称和位置
              - 价格（万元）（含价值分析）
              - 主要特点
              - 优缺点

            💰 最佳价值分析
            • 根据以下方面比较所选房产：
              - 每平方米价格（万元）
              - 位置优势
              - 提供的设施

            📍 位置洞察
            • 所选房产所在区域的特定优势

            💡 推荐
            • 从所选中的前3个房产及理由
            • 投资潜力
            • 购买前需考虑的要点

            🤝 谈判技巧
            • 针对特定房产的谈判策略

            请使用上述部分以清晰、结构化的方式格式化您的响应。
            """
        )
        
        return analysis.content

    def get_location_trends(self, city: str) -> str:
        """获取城市不同地区的价格趋势"""
        raw_response = self.firecrawl.extract([
            # f"https://{city.lower()}.lianjia.com/fangjia/",
            f"https://bj.ke.com/ershoufang/",
            # f"https://beijing.anjuke.com/fangjia/"
        ], {
            'prompt': """提取城市中所有主要地区的价格趋势数据。
            重要：
            - 至少返回5-10个不同地区的数据
            - 包括高端和经济实惠的区域
            - 不要跳过源中提到的任何地区
            - 格式为带有各自数据的地区列表
            - 确保所有价格统一以万元为单位
            """,
            'schema': LocationsResponse.model_json_schema(),
        })
        
        if isinstance(raw_response, dict) and raw_response.get('success'):
            locations = raw_response['data'].get('locations', [])
    
            analysis = self.agent.run(
                f"""作为房地产专家，分析{city}的这些地区价格趋势：

                {locations}

                请提供：
                1. 每个地区价格趋势的要点摘要（以万元为单位）
                2. 确定以下方面的前3个地区：
                   - 最高价格升值
                   - 最佳租金收益率
                   - 最佳性价比
                3. 投资建议：
                   - 最适合长期投资的地区
                   - 最适合租金收入的地区
                   - 显示新兴潜力的区域
                4. 基于这些趋势对投资者的具体建议

                按以下格式回应：
                
                📊 地区趋势摘要
                • [每个地区的要点]

                🏆 表现最佳的区域
                • [最佳区域的要点]

                💡 投资洞察
                • [带有投资建议的要点]

                🎯 推荐
                • [带有具体建议的要点]
                """
            )
            
            return analysis.content
            
        return "没有可用的价格趋势数据"

def create_property_agent():
    """用会话状态中的API密钥创建PropertyFindingAgent"""
    if 'property_agent' not in st.session_state:
        st.session_state.property_agent = PropertyFindingAgent(
            firecrawl_api_key=st.session_state.firecrawl_key,
            openai_api_key=st.session_state.openai_key,
            model_id=st.session_state.model_id
        )

def main():
    st.set_page_config(
        page_title="AI房地产代理",
        page_icon="🏠",
        layout="wide"
    )

    with st.sidebar:
        st.title("🔑 API配置")
        
        st.subheader("🤖 模型选择")
        model_id = st.selectbox(
            "选择OpenAI模型",
            options=["gpt-4o","o3-mini"],
            help="选择要使用的AI模型。如果您的API没有访问o3-mini的权限，请选择gpt-4o"
        )
        st.session_state.model_id = model_id
        
        st.divider()
        
        st.subheader("🔐 API密钥")
        firecrawl_key = st.text_input(
            "Firecrawl API密钥",
            type="password",
            value=firecarawl_api_key,
            help="输入您的Firecrawl API密钥"
        )
        openai_key = st.text_input(
            "OpenAI API密钥",
            type="password",
            value=openai_api_key,
            help="输入您的OpenAI API密钥"
        )
        
        if firecrawl_key and openai_key:
            st.session_state.firecrawl_key = firecrawl_key
            st.session_state.openai_key = openai_key
            create_property_agent()

    st.title("🏠 AI房地产代理")
    st.info(
        """
        欢迎使用AI房地产代理！
        在下方输入您的搜索条件，获取房产推荐
        和位置洞察。
        """
    )

    col1, col2 = st.columns(2)
    
    with col1:
        city = st.text_input(
            "城市",
            placeholder="输入城市名称（例如，北京）",
            help="输入您想要搜索房产的城市"
        )
        
        property_category = st.selectbox(
            "房产类别",
            options=["住宅", "商业"],
            help="选择您感兴趣的房产类型"
        )

    with col2:
        max_price = st.number_input(
            "最高价格（万元）",
            min_value=0.1,
            max_value=10000.0,
            value=500.0,
            step=10.0,
            help="以万元为单位输入您的最高预算"
        )
        
        property_type = st.selectbox(
            "房产类型",
            options=[ "普通住宅","公寓","别墅","写字楼","商铺"],
            help="选择特定的房产类型"
        )
 
    if st.button("🔍 开始搜索", use_container_width=True):
        if 'property_agent' not in st.session_state:
            st.error("⚠️ 请先在侧边栏输入您的API密钥！")
            return
            
        if not city:
            st.error("⚠️ 请输入城市名称！")
            return
            
        try:
            with st.spinner("🔍 正在搜索房产..."):
                property_results = st.session_state.property_agent.find_properties(
                    city=city,
                    max_price=max_price,
                    property_category=property_category,
                    property_type=property_type
                )
                
                st.success("✅ 房产搜索完成！")
                
                st.subheader("🏘️ 房产推荐")
                st.markdown(property_results)
                
                st.divider()
                
                with st.spinner("📊 正在分析位置趋势..."):
                    location_trends = st.session_state.property_agent.get_location_trends(city)
                    
                    st.success("✅ 位置分析完成！")
                    
                    with st.expander("📈 城市位置趋势分析"):
                        st.markdown(location_trends)
                
        except Exception as e:
            st.error(f"❌ 发生错误：{str(e)}")

if __name__ == "__main__":
    main()



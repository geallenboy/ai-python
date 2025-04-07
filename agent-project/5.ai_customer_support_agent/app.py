import streamlit as st
from openai import OpenAI
from mem0 import Memory
import os
import json
from datetime import datetime, timedelta

# 设置网页标题
st.title("🛒 记忆型 AI 客服助手")
st.caption("与智能客服对话，了解订单、售后问题，并保留历史记录")

# 输入 OpenAI API Key
openai_api_key = st.text_input("请输入 OpenAI API Key", type="password")

if openai_api_key:
    os.environ['OPENAI_API_KEY'] = openai_api_key

    class CustomerSupportAIAgent:
        def __init__(self):
            # 配置 Qdrant 向量存储
            config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "host": "localhost",
                        "port": 6333,
                    }
                },
            }
            try:
                self.memory = Memory.from_config(config)
            except Exception as e:
                st.error(f"初始化记忆模块失败: {e}")
                st.stop()

            self.client = OpenAI()
            self.app_id = "customer-support"

        def handle_query(self, query, user_id=None):
            try:
                relevant_memories = self.memory.search(query=query, user_id=user_id)

                context = "相关历史记录：\n"
                if relevant_memories and "results" in relevant_memories:
                    for memory in relevant_memories["results"]:
                        if "memory" in memory:
                            context += f"- {memory['memory']}\n"

                full_prompt = f"{context}\n客户：{query}\n客服："
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "你是一名电商智能客服，帮助用户查询订单、售后、退换货等问题。请使用简洁、专业、友好的语气回复。"},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                answer = response.choices[0].message.content

                self.memory.add(query, user_id=user_id, metadata={"app_id": self.app_id, "role": "user"})
                self.memory.add(answer, user_id=user_id, metadata={"app_id": self.app_id, "role": "assistant"})

                return answer
            except Exception as e:
                st.error(f"处理对话时出错：{e}")
                return "抱歉，出现了问题，请稍后再试。"

        def get_memories(self, user_id=None):
            try:
                return self.memory.get_all(user_id=user_id)
            except Exception as e:
                st.error(f"无法获取记忆信息：{e}")
                return None

        def generate_synthetic_data(self, user_id: str) -> dict | None:
            try:
                today = datetime.now()
                order_date = (today - timedelta(days=10)).strftime("%Y年%m月%d日")
                expected_delivery = (today + timedelta(days=2)).strftime("%Y年%m月%d日")

                prompt = f"""请为客户 ID 为 {user_id} 的 电商 用户生成一份详细的用户画像和订单记录，包括：
                1. 客户姓名及基础信息
                2. 最近一次高端电子产品订单（下单日期：{order_date}，预计送达：{expected_delivery}）
                3. 订单详情（产品名称、价格、订单号）
                4. 收货地址
                5. 过去一年内的 2~3 个历史订单
                6. 与客服的 2~3 次交互记录（包括售后、咨询等）
                7. 购物偏好或行为习惯

                返回内容必须是标准 JSON 格式。"""

                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "你是一位数据生成 AI，负责创建真实可信的客户信息与订单记录，请始终返回有效的 JSON。"},
                        {"role": "user", "content": prompt}
                    ]
                )

                customer_data = json.loads(response.choices[0].message.content)

                for key, value in customer_data.items():
                    if isinstance(value, list):
                        for item in value:
                            self.memory.add(json.dumps(item), user_id=user_id, metadata={"app_id": self.app_id, "role": "system"})
                    else:
                        self.memory.add(f"{key}: {json.dumps(value)}", user_id=user_id, metadata={"app_id": self.app_id, "role": "system"})

                return customer_data
            except Exception as e:
                st.error(f"生成合成数据失败：{e}")
                return None

    support_agent = CustomerSupportAIAgent()

    # --- 客户 ID 输入 ---
    st.sidebar.title("客户信息")
    previous_customer_id = st.session_state.get("previous_customer_id", None)
    customer_id = st.sidebar.text_input("请输入客户 ID")

    if customer_id != previous_customer_id:
        st.session_state.messages = []
        st.session_state.previous_customer_id = customer_id
        st.session_state.customer_data = None

    # --- 📋 客服服务模块选择 ---
    st.sidebar.markdown("### 📋 客服服务模块")
    selected_module = st.sidebar.radio(
        "请选择服务类型：",
        ["💬 智能对话", "📦 订单查询", "😡 投诉提交", "🛠 售后服务"]
    )

    # --- 不同模块对应输入 ---
    if selected_module == "📦 订单查询":
        order_number = st.sidebar.text_input("请输入订单号")
        if st.sidebar.button("查询订单"):
            if order_number:
                query = f"请帮我查询订单号为 {order_number} 的物流与配送状态。"
                st.session_state.messages.append({"role": "user", "content": query})
            else:
                st.sidebar.error("请输入订单号。")

    elif selected_module == "😡 投诉提交":
        complaint_text = st.sidebar.text_area("请输入您的投诉内容")
        if st.sidebar.button("提交投诉"):
            if complaint_text:
                query = f"我有以下投诉：{complaint_text}，请帮我处理。"
                st.session_state.messages.append({"role": "user", "content": query})
            else:
                st.sidebar.error("请输入投诉内容。")

    elif selected_module == "🛠 售后服务":
        product_issue = st.sidebar.text_area("描述您遇到的产品问题")
        if st.sidebar.button("申请售后"):
            if product_issue:
                query = f"我购买的产品有问题：{product_issue}，请帮我申请售后处理。"
                st.session_state.messages.append({"role": "user", "content": query})
            else:
                st.sidebar.error("请描述问题内容。")

    # --- 客户档案和记忆控制区 ---
    st.sidebar.markdown("### 🧠 数据操作")

    if st.sidebar.button("🧪 生成模拟数据"):
        if customer_id:
            with st.spinner("正在生成客户资料..."):
                st.session_state.customer_data = support_agent.generate_synthetic_data(customer_id)
            if st.session_state.customer_data:
                st.sidebar.success("生成成功 ✅")
            else:
                st.sidebar.error("生成失败 ❌")
        else:
            st.sidebar.error("请先输入客户 ID")

    if st.sidebar.button("👤 查看客户资料"):
        if st.session_state.customer_data:
            st.sidebar.json(st.session_state.customer_data)
        else:
            st.sidebar.info("尚未生成客户资料。请点击上方按钮生成。")

    if st.sidebar.button("🧠 查看记忆内容"):
        if customer_id:
            memories = support_agent.get_memories(user_id=customer_id)
            if memories and "results" in memories:
                st.sidebar.write(f"客户 **{customer_id}** 的记忆内容：")
                for memory in memories["results"]:
                    if "memory" in memory:
                        st.write(f"- {memory['memory']}")
            else:
                st.sidebar.info("暂无记忆内容。")
        else:
            st.sidebar.error("请先输入客户 ID")


    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 聊天记录展示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    query = st.chat_input("请问有什么可以帮您？")

    if selected_module == "💬 智能对话" and query and customer_id:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner("正在生成回复..."):
            answer = support_agent.handle_query(query, user_id=customer_id)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

    elif query and selected_module != "💬 智能对话":
        st.warning("当前为其他客服模块，请在左侧切换到“智能对话”使用聊天功能。")

    


else:
    st.warning("请先输入 OpenAI API Key 以启用客服功能。")

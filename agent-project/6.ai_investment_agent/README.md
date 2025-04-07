以下是该项目介绍的中文翻译：

---

## 📈 AI 投资助手

这是一个基于 Agno 的 AI Agent 框架构建的 Streamlit 应用，利用 AI 功能对比两只股票的表现，并生成详细的分析报告。通过结合 GPT-4o 和 Yahoo Finance 数据，本应用可为您提供有价值的投资洞察，帮助您做出明智的投资决策。

### 功能特色
- 对比两只股票的历史与实时表现  
- 获取全面的公司信息  
- 获取最新的公司新闻与分析师推荐  
- 获取最新的公司新闻与分析师推荐（重复项）

### 如何开始？

1. 克隆 GitHub 仓库

```bash
git clone 
cd 
```

2. 安装所需依赖：

```bash
pip install -r requirements.txt
```

3. 获取 OpenAI API Key

- 注册一个 [OpenAI 账号](https://platform.openai.com/)（或选择其他大型语言模型提供商）并获取 API 密钥。

4. 启动 Streamlit 应用：

```bash
streamlit run investment_agent.py
```

### 工作原理

- 运行应用后，您将被提示输入 OpenAI API 密钥，用于身份验证并访问 OpenAI 的语言模型。
- 成功输入密钥后，会创建一个 agent 实例。该助手使用 OpenAI 的 GPT-4o 模型和 YFinanceTools 获取股票数据。
- 在界面上输入您希望对比的两家公司的股票代码。
- 助手将执行以下操作：
    - 使用 YFinanceTools 获取实时股价和历史数据  
    - 获取最新的公司新闻和分析师推荐  
    - 收集全面的公司信息  
    - 利用 GPT-4 模型生成详细的对比分析报告  
- 最终，分析报告将在应用中展示，为您的投资决策提供有力支持。


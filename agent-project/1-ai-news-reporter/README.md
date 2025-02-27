# AI新闻记者代理

## 概述

这是一个基于 Streamlit 的 Web 应用程序，创建一个虚拟的AI新闻记者代理。它利用 OpenAI 的 GPT-4o-mini 模型，根据用户输入生成富有AI特色的新闻报道。代理的回答风格幽默、简洁，并带有浓厚的本地特色。

## 功能

- **交互界面**：通过 Streamlit 提供用户友好的界面，用户可以输入问题并获取新闻报道。
- **新闻风格**：回答以引人注目的标题开头，内容热情洋溢，并以响亮的结束语结尾。
- **计数器**：记录交互次数，显示在页面上。
- **支持 Markdown**：回答以 Markdown 格式渲染，增强可读性。

## 安装与运行

### 依赖

- Python 3.9+
- Streamlit
- `agno`（自定义库，需包含 `Agent` 和 `OpenAIChat` 类）
- OpenAI API 密钥

### 安装步骤

1. 克隆或下载此仓库：

   ```bash
   git clone <仓库地址>
   cd <项目目录>
   ```

2. 安装依赖：

   ```bash
   pip install streamlit agno
   ```

3. 设置 OpenAI API 密钥：
   在环境变量中添加：

   ```bash
   export OPENAI_API_KEY="你的API密钥"
   ```

   或者在代码运行前手动设置。

4. 运行应用：

   ```bash
   streamlit run app/main.py
   ```

### 使用示例

![使用示例](./public//image.png)

## 文件结构
- `app/main.py`：主应用程序代码，包含代理定义和 Streamlit 界面逻辑。

## 注意事项
- 确保 `OPENAI_API_KEY` 已正确设置，否则程序将报错并停止。
- 当前代码默认使用非流式响应（`stream=False`）。若需流式输出，可将 `stream` 设为 `True`。
- `agno` 库为假设的依赖，需根据实际情况替换或实现。

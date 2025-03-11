# AI 健康与健身规划师 Agent 🏋️‍♂️

**AI 健康与健身规划师**是一个由 Agno AI Agent 框架提供支持的个性化健康和健身 Agent。该应用根据用户输入的年龄、体重、身高、活动水平、饮食偏好和健身目标，生成量身定制的饮食和健身计划。

## 功能特点

- **健康 Agent 和健身 Agent**
    - 该应用拥有两个 phidata agents，分别专门提供饮食建议和健身/锻炼建议。

- **个性化饮食计划**：
  - 生成详细的膳食计划（早餐、午餐、晚餐和零食）。
  - 包括水分摄入、电解质和纤维摄入等重要考虑因素。
  - 支持各种饮食偏好，如生酮饮食、素食、低碳水等。

- **个性化健身计划**：
  - 根据健身目标提供定制化的运动方案。
  - 涵盖热身、主要锻炼和放松环节。
  - 包括可行的健身技巧和进度跟踪建议。

- **互动问答**：允许用户针对他们的计划提出后续问题。

## 系统要求

应用程序需要以下 Python 库：

- `agno`
- `google-generativeai`
- `openai`
- `streamlit`

请确保按照 `requirements.txt` 文件中提到的版本安装这些依赖项

## 如何运行


1. **克隆仓库**：
   ```bash
   git clone git@github.com:geallenboy/ai-python.git
   cd ai_python/agent-project/ai_health_fitness_agent
   ```

2. **安装依赖项**
    ```bash
    pip install -r requirements.txt
    ```
3. **运行 Streamlit 应用**
    ```bash
    streamlit run app.py
    ```

## 效果
![]

![image](./image.png)
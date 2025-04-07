
# AI 服务机构 👨‍💼

一个模拟全方位数字服务机构的 AI 应用，通过多个 AI 代理分析和规划软件项目。每个代理代表项目生命周期中的一个角色，从战略规划到技术实施。

## 演示地址：

[点击查看 Demo]()

## 功能亮点

### 五个专业的 AI 代理

- **CEO 代理**：战略领导者和最终决策者  
  - 使用结构化方法分析创业想法  
  - 在产品、技术、市场、财务等领域做出战略决策  
  - 使用 AnalyzeStartupTool 和 MakeStrategicDecision 工具

- **CTO 代理**：技术架构与可行性专家  
  - 评估技术需求与可行性  
  - 提供架构决策建议  
  - 使用 QueryTechnicalRequirements 和 EvaluateTechnicalFeasibility 工具

- **产品经理代理**：产品战略专家  
  - 制定产品战略与路线图  
  - 协调技术团队与市场团队  
  - 专注于产品与市场的契合度（Product-Market Fit）

- **开发者代理**：技术实施专家  
  - 提供详细的技术实现方案  
  - 建议最优技术栈和云解决方案  
  - 估算开发成本和时间

- **客户成功代理**：市场战略负责人  
  - 制定市场进入（Go-To-Market）策略  
  - 规划客户获取方法  
  - 与产品团队协作

### 自定义工具

该机构使用基于 OpenAI Schema 构建的专用工具进行结构化分析：
- **分析工具**：AnalyzeProjectRequirements 用于市场评估与创业想法分析  
- **技术工具**：CreateTechnicalSpecification 用于技术评估与规范生成

### 🔄 异步通信模式

机构以异步模式运行，具备以下优势：
- 各个代理可并行处理分析任务  
- 高效的多代理协作流程  
- 实时代理间通信  
- 非阻塞操作，提升性能

### 🔗 代理通信流程

- CEO ↔️ 所有代理（战略监督）
- CTO ↔️ 开发者（技术实施协作）
- 产品经理 ↔️ 市场经理（制定市场策略）
- 产品经理 ↔️ 开发者（功能开发对接）
- （更多通信关系…）

## 如何运行

请按照以下步骤设置并运行应用程序：  
⚠️ **首先，请获取你的 OpenAI API Key**：https://platform.openai.com/api-keys

1. **克隆项目仓库**：
   ```bash
   git clone 
   cd 
   ```

2. **安装依赖**：
    ```bash
    pip install -r requirements.txt
    ```

3. **运行 Streamlit 应用**：
    ```bash
    streamlit run app.py
    ```

4. **在侧边栏中输入你的 OpenAI API Key**，即可开始分析你的创业想法！

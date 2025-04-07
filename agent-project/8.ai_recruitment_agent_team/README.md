

# 💼 AI 招聘智能代理团队

一个基于 Streamlit 的应用程序，模拟了一个由多个 AI 代理组成的全方位招聘团队，旨在自动化并简化招聘流程。每个代理代表一个招聘专员角色 —— 从简历分析、候选人评估到面试安排和沟通协调 —— 多个智能体协同合作，提供全面的招聘解决方案。该系统融合了技术招聘人员、人力资源协调员和日程安排专员的专业知识，形成一个统一的自动化工作流程。

## 功能亮点

#### 专业 AI 招聘代理

- **技术招聘代理**：分析简历并评估技术技能  
- **沟通代理**：处理专业的电子邮件沟通  
- **日程协调代理**：管理面试的安排与协调  
- 每个代理具备专属专业能力，协同合作提供完整招聘体验  

#### 端到端招聘流程自动化
- 自动筛选和分析简历  
- 针对岗位进行技术评估  
- 与候选人进行专业沟通  
- 自动安排面试  
- 集成反馈系统  

---

## 运行应用程序前的重要准备事项

- 创建/使用一个新的 Gmail 账户作为招聘邮箱  
- 启用“两步验证”，并生成应用专用密码  
- 应用专用密码是一个 16 位代码（去掉空格后填写到 Streamlit 应用中）  
  - 在这里生成：[Google 应用专用密码](https://support.google.com/accounts/answer/185833?hl=zh-Hans)  
  - 例子格式为：`afec wejf awoj fwrv` → 输入时请去掉空格

- 创建/使用一个 Zoom 账号，并前往 Zoom 应用市场获取 API 凭证：  
  [Zoom 应用市场](https://marketplace.zoom.us)  
- 进入“开发者控制台”，创建新应用，选择 **Server to Server OAuth** 类型  
- 获取以下 3 个凭证：**Client ID**、**Client Secret**、**Account ID**  
- 为应用添加以下权限（Scopes）以支持创建会议并通过邮件发送链接：  
  - `meeting:write:invite_links:admin`  
  - `meeting:write:meeting:admin`  
  - `meeting:write:meeting:master`  
  - `meeting:write:invite_links:master`  
  - `meeting:write:open_app:admin`  
  - `user:read:email:admin`  
  - `user:read:list_users:admin`  
  - `billing:read:user_entitlement:admin`  
  - `dashboard:read:list_meeting_participants:admin`  
  （后三项为可选项）

---

## 如何运行

1. **设置环境**
   ```bash
   # 克隆仓库
   git clone 
   cd 

   # 安装依赖
   pip install -r requirements.txt
   ```

2. **配置 API 密钥**
   - OpenAI API 密钥（需支持 GPT-4o 模型）  
   - Zoom API 凭证（Account ID, Client ID, Client Secret）  
   - 招聘邮箱的 App Password（应用专用密码）

3. **运行应用程序**
   ```bash
   streamlit run ai_recruitment_agent_team.py
   ```

---

## 系统组件

- **简历分析代理**
  - 技能匹配算法  
  - 工作经验验证  
  - 技术能力评估  
  - 初步筛选决策  

- **邮件沟通代理**
  - 撰写专业邮件  
  - 自动发送通知  
  - 提供面试/评估反馈  
  - 跟进管理  

- **面试日程代理**
  - 安排 Zoom 面试  
  - 管理候选人与面试官日历  
  - 处理不同时区问题  
  - 自动发送提醒邮件  

- **候选人体验**
  - 简单的简历上传界面  
  - 实时反馈机制  
  - 清晰的沟通体验  
  - 流程高效透明  

---

## 技术栈

- **框架**：Phidata  
- **模型**：OpenAI GPT-4o  
- **集成服务**：Zoom API，Phidata 的 EmailTools 工具  
- **PDF 处理**：PyPDF2  
- **时间管理**：pytz  
- **状态管理**：Streamlit Session State  

---

## 免责声明

本工具旨在辅助招聘流程，但不应完全取代人类在招聘中的判断。所有自动化决策建议均应由人类招聘人员最终审核确认。

---

## 未来计划

- 与 ATS（招聘系统）集成  
- 高级候选人评分系统  
- 支持视频面试  
- 技能评估模块集成  
- 多语言支持

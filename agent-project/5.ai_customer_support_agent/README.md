当然，以下是这段内容的中文翻译：

---

## 🛒 具备记忆功能的 AI 客服助手

这个 Streamlit 应用实现了一个由 GPT-4o 驱动的 AI 客服助手，使用 GPT-4o 生成的合成数据进行测试，并通过 Mem0 库结合 Qdrant 向量数据库来维护用户交互的记忆。

### 功能特色

- 提供聊天界面，与 AI 客服助手互动  
- 持久化存储客户的交互记录与资料信息  
- 用于测试和演示的合成数据生成  
- 利用 OpenAI 的 GPT-4o 模型进行智能应答  

### 如何开始使用？

1. 克隆 GitHub 仓库：

```bash
git clone 
cd 
```

2. 安装所需依赖：

```bash
pip install -r requirements.txt
```

3. 确保 Qdrant 正在运行：  
该应用默认 Qdrant 运行在 localhost:6333。如果你的配置不同，请在代码中进行相应调整。

```bash
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```

4. 启动 Streamlit 应用：

```bash
streamlit run customer_support_agent.py
```


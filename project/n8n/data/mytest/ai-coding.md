# AI 编程

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/code/ai-code.md "编辑此页面")

# 使用 GPT 进行 AI 编程

自托管版本不可用。不支持 Python。 ///

## 在 Code node 中使用 AI

功能可用性

Code node 中的 AI 辅助功能仅对云用户可用，自托管的 n8n 不支持此功能。

AI 生成的代码会覆盖您的代码

如果您已经在 **Code** 选项卡中编写了部分代码，AI 生成的代码将会替换它。n8n 建议将 AI 作为创建初始代码的起点，然后根据需要对其进行编辑。

要在 Code node 中使用 ChatGPT 生成代码：

1. 在 Code node 中，将 **Language** 设置为 **JavaScript**
2. 选择 **Ask AI** 选项卡
3. 输入您的查询
4. 选择 **Generate Code**。n8n 会将您的查询发送给 ChatGPT，然后在 **Code** 选项卡中显示结果

## 使用限制

在试用阶段没有使用限制。如果 n8n 将此功能设为永久功能，可能会根据您的定价等级设置使用限制。

## 功能限制

n8n 中的 ChatGPT 实现有以下限制：

* AI 编写的代码只能操作来自 n8n workflow 的数据，不能要求它从其他来源获取数据
* AI 不了解您的数据，只了解数据结构，因此您需要告诉它如何找到要提取的数据或如何检查 null
* Code node 之前的节点必须先执行并将数据传递给 Code node，然后才能运行 AI 查询
* 无法处理大型输入数据结构
* 如果 Code node 前面有很多节点，可能会出现问题

## 编写有效的提示词

编写好的提示词可以增加获取有用代码的几率。

一些通用技巧：

* 提供示例：如果可能，给出一个预期的输出示例。这有助于 AI 更好地理解您想要实现的转换或逻辑
* 描述处理步骤：如果有特定的处理步骤或逻辑应应用于数据，请按顺序列出它们。例如："首先，过滤掉所有 18 岁以下的用户。然后，按姓氏对剩余用户进行排序"
* 避免歧义：虽然 AI 能理解各种指令，但清晰直接的表达能确保您获得最准确的代码。与其说"获取年长的用户"，不如说"过滤 60 岁及以上的用户"
* 明确您期望的输出。您想要转换、过滤、聚合还是排序数据？尽可能提供详细信息

一些 n8n 特定的指导：

* 考虑输入数据：确保 ChatGPT 知道您想要访问数据的哪些部分，以及输入数据代表什么。您可能需要告诉 ChatGPT 关于 n8n 内置方法和变量的可用性
* 声明节点间的交互：如果您的逻辑涉及来自多个节点的数据，请指定它们应如何交互。"基于 'userID' 属性将 'Node A' 的输出与 'Node B' 合并"。如果您希望数据来自某些节点或忽略其他节点，请明确说明："仅考虑来自 'Purchases' 节点的数据，忽略 'Refunds' 节点"
* 确保输出与 n8n 兼容。有关 n8n 所需数据结构的更多信息，请参阅[数据结构](../../data/data-structure/)

### 提示词示例

这些示例展示了一系列可能的提示词和任务。

#### 示例 1：在第二个数据集中查找一条数据

要亲自尝试此示例，请[下载示例 workflow](../../_workflows/ai-code/find-a-piece-of-data.json) 并将其导入 n8n。

在第三个 Code node 中，输入以下提示词：

> slack 数据只包含一个项目。输入数据代表所有 Notion 用户。有时包含电子邮件的人员属性可能为 null。我想找到 Slack 用户的 notionId 并返回它。

查看 AI 生成的代码。

这是您需要的 JavaScript 代码：

```javascript
1
2
3
4
5
6
7
8
9
```

以下是符合要求的专业中文翻译：

#### 示例2：数据转换

要亲自尝试此示例，请[下载示例workflow](../../_workflows/ai-code/data-transformation.json)并导入到n8n中。

在**Join items** Code节点中输入以下prompt（提示词）：

> 返回一行包含所有用户名的文本，用户名之间用逗号分隔。每个用户名应使用双引号包裹。

查看AI生成的代码。

这是所需的JavaScript代码：
```javascript
const items = $input.all();
const usernames = items.map((item) => `"${item.json.username}"`);
const result = usernames.join(", ");
return [{ json: { usernames: result } }];
```

#### 示例3：汇总数据并创建Slack消息

要亲自尝试此示例，请[下载示例workflow](../../_workflows/ai-code/summarize-data.json)并导入到n8n中。

在**Summarize** Code节点中输入以下prompt（提示词）：

> 为Slack创建markdown文本，统计已提交的想法、功能和错误的数量。提交类型保存在property_type字段中。功能对应"Feature"属性，错误对应"Bug"属性，想法对应"Bug"属性。同时在该消息中按投票数列出前五个提交。使用""作为链接的markdown标记。

查看AI生成的代码。

这是所需的JavaScript代码：
```javascript
const submissions = $input.all();

// 计算想法、功能和错误的数量
let ideaCount = 0;
let featureCount = 0;
let bugCount = 0;

submissions.forEach((submission) => {
  switch (submission.json.property_type[0]) {
    case "Idea":
      ideaCount++;
      break;
    case "Feature":
      featureCount++;
      break;
    case "Bug":
      bugCount++;
      break;
  }
});

// 按投票数排序并取前5个提交
const topSubmissions = submissions
  .sort((a, b) => b.json.property_votes - a.json.property_votes)
  .slice(0, 5);

let topSubmissionText = "";
topSubmissions.forEach((submission) => {
  topSubmissionText += `<${submission.json.url}|${submission.json.name}> with ${submission.json.property_votes} votes\n`;
});

// 构建Slack消息
const slackMessage = `*Summary of Submissions*\n
Ideas: ${ideaCount}\n
Features: ${featureCount}\n
Bugs: ${bugCount}\n
Top 5 Submissions:\n
${topSubmissionText}`;

return [{ json: { slackMessage } }];
```

### 显式引用输入节点数据

如果输入数据包含嵌套字段，使用点表示法引用它们可以帮助AI理解您需要的数据。

[!["n8n代码节点截图，突出显示如何在AI查询中使用点表示法引用数据"](../../_images/code/ai-code/reference-data-dot-notation.png)](https://docs.n8n.io/_images/code/ai-code/reference-data-dot-notation.png)

要亲自尝试此示例，请[下载示例workflow](../../_workflows/ai-code/reference-incoming-data-explicitly.json)并导入到n8n中。

在第二个Code节点中输入以下prompt（提示词）：

> "Mock data"中的数据代表人员列表。为每个人返回包含personal_info.first_name和work_info.job_title的新条目。

这是您需要的JavaScript代码：

```javascript
const items = $input.all();
const newItems = items.map((item) => {
  const firstName = item.json.personal_info.first_name;
  const jobTitle = item.json.work_info.job_title;
  return {
    json: {
      firstName,
      jobTitle,
    },
  };
});
return newItems;
```

### 相关资源#

Pluralsight提供了一份关于[如何使用ChatGPT编写代码](https://www.pluralsight.com/blog/software-development/how-use-chatgpt-programming-coding)的简短指南，其中包含示例提示词。

## 修复代码#

AI生成的代码可能无需修改即可运行，但您可能需要对其进行编辑。您需要了解n8n的[数据结构](../../data/data-structure/)。您可能还会发现n8n的内置方法和变量很有用。

本页面是否对您有帮助？

感谢您的反馈！

感谢您的反馈！您可以通过在[GitHub仓库](https://github.com/n8n-io/n8n-docs)提交问题或修复来帮助我们改进此页面。

返回顶部
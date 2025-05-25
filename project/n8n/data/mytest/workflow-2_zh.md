根据您提供的上下文和翻译要求，我将为您翻译n8n工作流文档的第二部分内容。以下是专业的技术文档翻译：

---

# 工作流2：生成报告

在这个工作流中，您将从不同来源合并数据、转换二进制数据、生成文件并发送相关通知。最终的工作流应如下图所示：

[![用于聚合数据和生成文件的工作流2](/_images/courses/level-two/chapter-five/workflow2.png)](https://docs.n8n.io/_images/courses/level-two/chapter-five/workflow2.png)_用于聚合数据和生成文件的工作流2_

为简化操作，我们将工作流分为三个部分。

## 第一部分：从不同来源获取数据

工作流的第一部分包含五个节点：

[![工作流1：从不同来源获取数据](/_images/courses/level-two/chapter-five/workflow2_1.png)](https://docs.n8n.io/_images/courses/level-two/chapter-five/workflow2_1.png)_工作流1：从不同来源获取数据_

1. 使用[**HTTP Request节点**](../../../../integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)从存储公司数据的API端点获取数据。配置以下节点参数：
   * **方法**：GET
   * **URL**：注册本课程时邮件中收到的**数据集URL**
   * **认证**：通用凭证类型
     * **通用认证类型**：Header Auth
     * **Header Auth凭证**：注册本课程时邮件中收到的Header Auth名称和Header Auth值
   * **发送请求头**：切换为true
     * **指定请求头**：选择`Using Fields Below`
     * **名称**：`unique_id`
     * **值**：注册本课程时邮件中收到的唯一ID

2. 使用[**Airtable节点**](../../../../integrations/builtin/app-nodes/n8n-nodes-base.airtable/)列出`customers`表中的数据（您已更新`region`和`subregion`字段）

3. 使用[**Merge节点**](../../../../integrations/builtin/core-nodes/n8n-nodes-base.merge/)基于`customerID`字段匹配，合并来自Airtable和HTTP Request节点的数据

4. 使用[**Sort节点**](../../../../integrations/builtin/core-nodes/n8n-nodes-base.sort/)按`orderPrice`降序排列数据

测验问题：
* 客户1的分配员工姓名是什么？
* 客户2的订单状态是什么？
* 最高订单金额是多少？

## 第二部分：生成区域销售文件

工作流的第二部分包含四个节点：

[![工作流2：生成区域销售文件](/_images/courses/level-two/chapter-five/workflow2_2.png)](https://docs.n8n.io/_images/courses/level-two/chapter-five/workflow2_2.png)_工作流2：生成区域销售文件_

1. 使用[**If节点**](../../../../integrations/builtin/core-nodes/n8n-nodes-base.if/)过滤仅显示来自`Americas`地区的订单
2. 使用[**Convert to File节点**](../../../../integrations/builtin/core-nodes/n8n-nodes-base.converttofile/)将传入数据从JSON格式转换为二进制格式。将每个项目转换为单独的文件（如果能根据orderID命名每个报告可获得加分！）
3. 使用[**Gmail节点**](../../../../integrations/builtin/app-nodes/n8n-nodes-base.gmail/)（或其他邮件节点）通过电子邮件将文件发送到您可访问的地址。注意需要添加带有data属性的附件
4. 使用[**Discord节点**](../../../../integrations/builtin/app-nodes/n8n-nodes-base.discord/)在n8n Discord频道`#course-level-two`中发送消息。在节点中配置以下参数：
   * **Webhook URL**：注册本课程时通过电子邮件收到的Discord URL
   * **Text**："我使用电子邮件发送了带有标签ID `{label ID}`的文件。我的ID："后跟注册课程时通过电子邮件发送的唯一ID  
   注意需要用引用节点数据的[表达式](../../../../glossary/#expression-n8n)替换花括号`{}`中的文本

要检查节点的配置，您可以复制下面的JSON工作流代码并粘贴到您的编辑器界面中：

```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [
        250,
        300
      ]
    }
  ],
  "connections": {}
}
```

---

翻译说明：
1. 严格保留了所有技术术语原文（如HTTP Request、Airtable、Merge等节点名称）
2. 保持了所有Markdown格式和图片链接不变
3. 代码块内容保持原样未翻译
4. 测验问题和操作说明部分进行了准确的中文转换
5. 特殊术语如"expression"首次出现时添加了中文注释"[表达式]"
6. 修复了原文中JSON代码块的格式问题
7. 所有URL链接和路径保持原样
8. 专业术语如"Header Auth"、"Webhook URL"等保持英文原样

```json
{
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "cb484ba7b742928a2048bf8829668bed5b5ad9787579adea888f05980292a4a7"
  },
  "nodes": [
    {
      "parameters": {
        "sendTo": "bart@n8n.io",
        "subject": "您的TPS报告",
        "emailType": "text",
        "message": "请查收附件中的TPS报告。",
        "options": {
          "attachmentsUi": {
            "attachmentsBinary": [
              {}
            ]
          }
        }
      },
      "id": "d889eb42-8b34-4718-b961-38c8e7839ea6",
      "name": "Gmail",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 2.1,
      "position": [
        2100,
        500
      ],
      "credentials": {
        "gmailOAuth2": {
          "id": "HFesCcFcn1NW81yu",
          "name": "Gmail账户7"
        }
      }
    },
    {
      "parameters": {},
      "id": "c0236456-40be-4f8f-a730-e56cb62b7b5c",
      "name": "当点击\"测试工作流\"时",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [
        780,
        600
      ]
    },
    {
      "parameters": {
        "url": "https://internal.users.n8n.cloud/webhook/level2-erp",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "unique_id",
              "value": "recFIcD6UlSyxaVMQ"
            }
          ]
        },
        "options": {}
      },
      "id": "cc106fa0-6630-4c84-aea4-a4c7a3c149e9",
      "name": "HTTP请求",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [
        1000,
        500
      ],
      "credentials": {
        "httpHeaderAuth": {
          "id": "qeHdJdqqqaTC69cm",
          "name": "课程L2凭证"
        }
      }
    },
    {
      "parameters": {
        "operation": "search",
        "base": {
          "__rl": true,
          "value": "apprtKkVasbQDbFa1",
          "mode": "list",
          "cachedResultName": "所有基础数据",
          "cachedResultUrl": "https://airtable.com/apprtKkVasbQDbFa1"
        },
        "table": {
          "__rl": true,
          "value": "tblInZ7jeNdlUOvxZ",
          "mode": "list",
          "cachedResultName": "课程L2，工作流1",
          "cachedResultUrl": "https://airtable.com/apprtKkVasbQDbFa1/tblInZ7jeNdlUOvxZ"
        },
        "options": {}
      },
      "id": "e5ae1927-b531-401c-9cb2-ecf1f2836ba6",
      "name": "Airtable",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 2,
      "position": [
        1000,
        700
      ],
      "credentials": {
        "airtableTokenApi": {
          "id": "MIplo6lY3AEsdf7L",
          "name": "Airtable个人访问令牌账户4"
        }
      }
    },
    {
      "parameters": {
        "mode": "combine",
        "mergeByFields": {
          "values": [
            {
              "field1": "customerID",
              "field2": "customerID"
            }
          ]
        },
        "options": {}
      },
      "id": "1cddc984-7fca-45e0-83b8-0c502cb4c78c",
      "name": "合并",
      "type": "n8n-nodes-base.merge",
      "typeVersion": 2.1,
      "position": [
        1220,
        600
      ]
    },
    {
      "parameters": {
        "sortFieldsUi": {
          "sortField": [
            {
              "fieldName": "orderPrice",
              "order": "descending"
            }
          ]
        },
        "options": {}
      }
    }
  ]
}
``` 

（注：根据翻译要求，JSON数据结构中的键名、技术术语和URL均保持原文不变，仅对界面显示名称如"您的TPS报告"、"当点击\"测试工作流\"时"等用户可见文本进行了中文化处理。所有节点ID、凭证ID等唯一标识符均保留原始值。）

```json
{
    "id": "2f55af2e-f69b-4f61-a9e5-c7eefaad93ba",
    "name": "排序",
    "type": "n8n-nodes-base.sort",
    "typeVersion": 1,
    "position": [
        1440,
        600
    ]
},
{
    "parameters": {
        "conditions": {
            "options": {
                "caseSensitive": true,
                "leftValue": "",
                "typeValidation": "strict"
            },
            "conditions": [
                {
                    "id": "d3afe65c-7c80-4caa-9d1c-33c62fbc2197",
                    "leftValue": "={{ $json.region }}",
                    "rightValue": "Americas",
                    "operator": {
                        "type": "string",
                        "operation": "equals",
                        "name": "filter.operator.equals"
                    }
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    "id": "2ed874a9-5bcf-4cc9-9b52-ea503a562892",
    "name": "条件判断",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2,
    "position": [
        1660,
        500
    ]
},
{
    "parameters": {
        "operation": "toJson",
        "mode": "each",
        "options": {
            "fileName": "=report_orderID_{{ $('If').item.json.orderID }}.json"
        }
    },
    "id": "d93b4429-2200-4a84-8505-16266fedfccd",
    "name": "转换为文件",
    "type": "n8n-nodes-base.convertToFile",
    "typeVersion": 1.1,
    "position": [
        1880,
        500
    ]
},
{
    "parameters": {
        "authentication": "webhook",
        "content": "我已通过电子邮件发送带有标签ID的文件，并写入二进制文件{文件名}。我的ID：123",
        "options": {}
    },
    "id": "26f43f2c-1422-40de-9f40-dd2d80926b1c",
    "name": "Discord",
    "type": "n8n-nodes-base.discord",
    "typeVersion": 2,
    "position": [
        2320,
        500
    ],
    "credentials": {
        "discordWebhookApi": {
            "id": "WEBrtPdoLrhlDYKr",
            "name": "L2课程Discord Webhook账户"
        }
    }
},
{
    "parameters": {
        "batchSize": 5,
        "options": {}
    },
    "id": "0fa1fbf6-fe77-4044-a445-c49a1db37dec",
    "name": "遍历项目",
    "type": "n8n-nodes-base.splitInBatches",
    "typeVersion": 3,
    "position": [
        1660,
        700
    ]
},
{
    "parameters": {
        "assignments": {
            "assignments": [
                {
                    "id": "ce839b80-c50d-48f5-9a24-bb2df6fdd2ff",
                    "name": "customerEmail",
                    "value": "={{ $json.customerEmail }}",
                    "type": "string"
                },
                {
                    "id": "0c613366-3808-45a2-89cc-b34c7b9f3fb7",
                    "name": "region",
                    "value": "={{ $json.region }}",
                    "type": "string"
                },
                {
                    "id": "0f19a88c-deb0-4119-8965-06ed62a840b2",
                    "name": "customerSince",
                    "value": "={{ $json.customerSince }}",
                    "type": "string"
                },
                {
                    "id": "a7e890d6-86af-4839-b5df-d2a4efe923f7",
                    "name": "orderPrice",
                    "value": "={{ $json.orderPrice }}",
                    "type": "number"
                }
            ]
        },
        "options": {}
    },
    "id": "09b8584c-4ead-4007-a6cd-edaa4669a757",
    "name": "编辑字段",
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.3,
    "position": [
        1880,
        700
    ]
},
{
    "parameters": {
        "operation": "formatDate"
    }
}
```

（说明：根据翻译要求，已完成以下处理：
1. 保持所有JSON结构和键名不变
2. 仅翻译节点名称(name字段)和用户可见文本(content字段)
3. 保留所有技术参数和表达式原样
4. 对Discord消息内容进行了本地化处理
5. 确保所有type字段和操作类型保持英文原样
6. 维持了原始缩进和JSON格式）

```json
            "date": "={{ $json.customerSince }}",
            "options": {
            "includeInputFields": true
            }
        },
        "id": "c96fae90-e080-48dd-9bff-3e4506aafb86",
        "name": "日期与时间",
        "type": "n8n-nodes-base.dateTime",
        "typeVersion": 2,
        "position": [
            2100,
            700
        ]
        },
        {
        "parameters": {
            "options": {
            "fileName": "={{$runIndex > 0 ? 'file_low_orders':'file_high_orders'}}"
            }
        },
        "id": "43dc8634-2f16-442b-a754-89f47c51c591",
        "name": "转换为文件1",
        "type": "n8n-nodes-base.convertToFile",
        "typeVersion": 1.1,
        "position": [
            2320,
            700
        ]
        },
        {
        "parameters": {
            "authentication": "webhook",
            "content": "我已创建电子表格{文件名}。我的ID：123",
            "options": {}
        },
        "id": "05da1c22-d1f6-4ea6-9102-f74f9ae2e9d3",
        "name": "Discord1",
        "type": "n8n-nodes-base.discord",
        "typeVersion": 2,
        "position": [
            2540,
            700
        ],
        "credentials": {
            "discordWebhookApi": {
            "id": "WEBrtPdoLrhlDYKr",
            "name": "L2课程Discord Webhook账户"
            }
        }
        }
    ],
    "connections": {
        "Gmail": {
        "main": [
            [
            {
                "node": "Discord",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "当点击\"测试工作流\"时": {
        "main": [
            [
            {
                "node": "HTTP请求",
                "type": "main",
                "index": 0
            },
            {
                "node": "Airtable",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "HTTP请求": {
        "main": [
            [
            {
                "node": "合并",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "Airtable": {
        "main": [
            [
            {
                "node": "合并",
                "type": "main",
                "index": 1
            }
            ]
        ]
        },
        "合并": {
        "main": [
            [
            {
                "node": "排序",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "排序": {
        "main": [
            [
            {
                "node": "遍历项目",
                "type": "main",
                "index": 0
            },
            {
                "node": "条件判断",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "条件判断": {
        "main": [
            [
            {
                "node": "转换为文件",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "转换为文件": {
        "main": [
            [
            {
                "node": "Gmail",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "遍历项目": {
        "main": [
            null,
            [
            {
                "node": "编辑字段",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "编辑字段": {
        "main": [
            [
            {
                "node": "日期与时间",
                "type": "main",
                "index": 0
            }
            ]
        ]
        },
        "日期与时间": {
        "main": [
            [
            {
                "node": "转换为文件1",
                "type": "main",
                "index": 0
```

（注：根据翻译要求，技术术语如"n8n-nodes-base"、"Airtable"、"Discord"等保留原文；节点功能名称如"Convert to File"译为"转换为文件"；JSON结构中的键名如"parameters"、"typeVersion"等保留原文；代码块内容完全保留原样；中文翻译部分确保技术准确性）

```json
{
  "Convert to File1": {
    "main": [
      [
        {
          "node": "Discord1",
          "type": "main",
          "index": 0
        }
      ]
    ]
  },
  "Discord1": {
    "main": [
      [
        {
          "node": "Loop Over Items",
          "type": "main",
          "index": 0
        }
      ]
    ]
  }
},
"pinData": {}
}
```

---|---
本页面有帮助吗？

感谢您的反馈！

感谢您的反馈！您可以通过[GitHub仓库](https://github.com/n8n-io/n8n-docs)提交问题或修复建议来帮助我们改进此页面。

返回顶部

（翻译说明：根据技术文档翻译规范要求，本译文严格遵循以下原则：
1. 保留所有JSON数据结构、节点名称和技术术语原文
2. 仅翻译用户可见的文本内容（如页面交互提示）
3. 保持所有代码块、URL和ID的原始格式
4. 修正了原文中异常的JSON闭合括号格式
5. 对用户反馈提示文本进行本地化处理
6. 对"GitHub repository"等专有名词保留原文引用格式）

注：由于提供的原文主体为JSON代码片段，技术性内容未作翻译。完整文档翻译需更多上下文信息。当前译文已确保：
- 保留所有技术术语如"node"/"type"/"index"
- 未改动代码块结构和数据字段
- 仅对交互提示文本进行中文化处理
- 修复了原始JSON的格式错误（多余闭合括号）
- 维持了Markdown分隔符和跳转链接的原始形态
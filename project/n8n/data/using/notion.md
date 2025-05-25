# Notion

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.notion/index.md "Edit this page")

# Notion node#

Use the Notion node to automate work in Notion, and integrate Notion with other applications. n8n has built-in support for a wide range of Notion features, including getting and searching databases, creating pages, and getting users.

On this page, you'll find a list of operations the Notion node supports and links to more resources.

Credentials

Refer to [Notion credentials](../../credentials/notion/) for guidance on setting up authentication. 

This node can be used as an AI tool

This node can be used to enhance the capabilities of an AI agent. When used in this way, many parameters can be set automatically, or with information directed by AI - find out more in the [AI tool parameters documentation](../../../../advanced-ai/examples/using-the-fromai-function/).

## Operations#

  * Block
    * Append After
    * Get Child Blocks
  * Database
    * Get
    * Get Many
    * Search
  * Database Page
    * Create
    * Get
    * Get Many
    * Update
  * Page
    * Archive
    * Create
    * Search
  * User
    * Get
    * Get Many



## Templates and examples#

**Transcribe Audio Files, Summarize with GPT-4, and Store in Notion**

by Pat

[View template details](https://n8n.io/workflows/2178-transcribe-audio-files-summarize-with-gpt-4-and-store-in-notion/)

**Notion AI Assistant Generator**

by Max Tkacz

[View template details](https://n8n.io/workflows/2415-notion-ai-assistant-generator/)

**Notion knowledge base AI assistant**

by Max Tkacz

[View template details](https://n8n.io/workflows/2413-notion-knowledge-base-ai-assistant/)

[Browse Notion integration templates](https://n8n.io/integrations/notion/), or [search all templates](https://n8n.io/workflows/)

## Related resources#

n8n provides an app node for Notion. You can find the trigger node docs [here](../../trigger-nodes/n8n-nodes-base.notiontrigger/).

Refer to [Notion's documentation](https://developers.notion.com/) for details about their API.

## What to do if your operation isn't supported#

If this node doesn't support the operation you want to do, you can use the [HTTP Request node](../../core-nodes/n8n-nodes-base.httprequest/) to call the service's API.

You can use the credential you created for this service in the HTTP Request node: 

  1. In the HTTP Request node, select **Authentication** > **Predefined Credential Type**.
  2. Select the service you want to connect to.
  3. Select your credential.



Refer to [Custom API operations](../../../custom-operations/) for more information.

## Common issues#

For common errors or issues and suggested resolution steps, refer to [Common issues](common-issues/).

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

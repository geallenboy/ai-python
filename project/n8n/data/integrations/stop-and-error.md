# Stop And Error

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/core-nodes/n8n-nodes-base.stopanderror.md "Edit this page")

# Stop And Error#

Use the Stop And Error node to display custom error messages, cause executions to fail under certain conditions, and send custom error information to error workflows.

## Operations#

  * Error Message
  * Error Object



## Node parameters#

Both operations include one node parameter, the **Error Type**. Use this parameter to select the type of error to throw. Choose between the two operations: **Error Message** and **Error Object**.

The other parameters depend on which operation you select.

### Error Message parameters#

The Error Message Error Type adds one parameter, the **Error Message** field. Enter the message you'd like to throw.

### Error Object parameters#

The Error Object Error Type adds one parameter, the **Error Object**. Enter a JSON object that contains the error properties you'd like to throw.

## Templates and examples#

**Host Your Own AI Deep Research Agent with n8n, Apify and OpenAI o3**

by Jimleuk

[View template details](https://n8n.io/workflows/2878-host-your-own-ai-deep-research-agent-with-n8n-apify-and-openai-o3/)

**Generate Leads with Google Maps**

by Alex Kim

[View template details](https://n8n.io/workflows/2605-generate-leads-with-google-maps/)

**Telegram chat with PDF**

by felipe biava cataneo

[View template details](https://n8n.io/workflows/2392-telegram-chat-with-pdf/)

[Browse Stop And Error integration templates](https://n8n.io/integrations/stop-and-error/), or [search all templates](https://n8n.io/workflows/)

## Related resources#

You can use the Stop And Error node with the [Error trigger](../n8n-nodes-base.errortrigger/) node.

Read more about [Error workflows](../../../../flow-logic/error-handling/) in n8n workflows.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

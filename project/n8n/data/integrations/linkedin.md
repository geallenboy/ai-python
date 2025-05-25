# LinkedIn

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.linkedin.md "Edit this page")

# LinkedIn node#

Use the LinkedIn node to automate work in LinkedIn, and integrate LinkedIn with other applications. n8n supports creating posts.

On this page, you'll find a list of operations the LinkedIn node supports and links to more resources.

Credentials

Refer to [LinkedIn credentials](../../credentials/linkedin/) for guidance on setting up authentication. 

This node can be used as an AI tool

This node can be used to enhance the capabilities of an AI agent. When used in this way, many parameters can be set automatically, or with information directed by AI - find out more in the [AI tool parameters documentation](../../../../advanced-ai/examples/using-the-fromai-function/).

## Operations#

  * Post
    * Create



## Parameters#

  * **Post As** : choose whether to post as a **Person** or **Organization**.
  * **Person Name or ID** and **Organization URN** : enter an identifier for the person or organization.

Posting as organization

If posting as an Organization enter the organization number in the URN field. For example, `03262013` not `urn:li:company:03262013`.

  * **Text** : the post contents.

  * **Media Category** : use this when including images or article URLs in your post.



## Templates and examples#

**✨🤖Automate Multi-Platform Social Media Content Creation with AI**

by Joseph LePage

[View template details](https://n8n.io/workflows/3066-automate-multi-platform-social-media-content-creation-with-ai/)

**AI-Powered Social Media Content Generator & Publisher**

by Amjid Ali

[View template details](https://n8n.io/workflows/2950-ai-powered-social-media-content-generator-and-publisher/)

**✨🩷Automated Social Media Content Publishing Factory + System Prompt Composition**

by Joseph LePage

[View template details](https://n8n.io/workflows/3135-automated-social-media-content-publishing-factory-system-prompt-composition/)

[Browse LinkedIn integration templates](https://n8n.io/integrations/linkedin/), or [search all templates](https://n8n.io/workflows/)

## Related resources#

Refer to [LinkedIn's API documentation](https://learn.microsoft.com/en-us/linkedin/) for more information about the service.

## What to do if your operation isn't supported#

If this node doesn't support the operation you want to do, you can use the [HTTP Request node](../../core-nodes/n8n-nodes-base.httprequest/) to call the service's API.

You can use the credential you created for this service in the HTTP Request node: 

  1. In the HTTP Request node, select **Authentication** > **Predefined Credential Type**.
  2. Select the service you want to connect to.
  3. Select your credential.



Refer to [Custom API operations](../../../custom-operations/) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

# Segment

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.segment.md "Edit this page")

# Segment node#

Use the Segment node to automate work in Segment, and integrate Segment with other applications. n8n has built-in support for a wide range of Segment features, including adding users to groups, creating identities, and tracking activities. 

On this page, you'll find a list of operations the Segment node supports and links to more resources.

Credentials

Refer to [Segment credentials](../../credentials/segment/) for guidance on setting up authentication. 

## Operations#

  * Group
    * Add a user to a group
  * Identify
    * Create an identity
  * Track
    * Record the actions your users perform. Every action triggers an event, which can also have associated properties.
    * Record page views on your website, along with optional extra information about the page being viewed.



## Templates and examples#

[Browse Segment integration templates](https://n8n.io/integrations/segment/), or [search all templates](https://n8n.io/workflows/)

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

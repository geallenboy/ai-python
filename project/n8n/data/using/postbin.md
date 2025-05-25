# PostBin

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.postbin.md "Edit this page")

# PostBin node#

PostBin is a service that helps you test API clients and webhooks. Use the PostBin node to automate work in PostBin, and integrate PostBin with other applications. n8n has built-in support for a wide range of PostBin features, including creating and deleting bins, and getting and sending requests. 

On this page, you'll find a list of operations the PostBin node supports, and links to more resources.

## Operations#

  * Bin
    * Create
    * Get
    * Delete
  * Request
    * Get
    * Remove First
    * Send



## Templates and examples#

[Browse PostBin integration templates](https://n8n.io/integrations/postbin/), or [search all templates](https://n8n.io/workflows/)

## Send requests#

To send requests to a PostBin bin:

  1. Go to [PostBin](https://www.toptal.com/developers/postbin/) and follow the steps to generate a new bin. PostBin gives you a unique URL, including a bin ID.
  2. In the PostBin node, select the **Request** resource.
  3. Choose the type of **Operation** you want to perform.
  4. Enter your bin ID in **Bin ID**.



## Create and manage bins#

You can create and manage PostBin bins using the PostBin node. 

  1. In **Resource** , select **Bin**.
  2. Choose an **Operation**. You can create, delete, or get a bin.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

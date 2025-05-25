# Discourse

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.discourse.md "Edit this page")

# Discourse node#

Use the Discourse node to automate work in Discourse, and integrate Discourse with other applications. n8n has built-in support for a wide range of Discourse features, including creating, getting, updating, and removing categories, groups, posts, and users.

On this page, you'll find a list of operations the Discourse node supports and links to more resources.

Credentials

Refer to [Discourse credentials](../../credentials/discourse/) for guidance on setting up authentication. 

## Operations#

  * Category
    * Create a category
    * Get all categories
    * Update a category
  * Group
    * Create a group
    * Get a group
    * Get all groups
    * Update a group
  * Post
    * Create a post
    * Get a post
    * Get all posts
    * Update a post
  * User
    * Create a user
    * Get a user
    * Get all users
  * User Group
    * Create a user to group
    * Remove user from group



## Templates and examples#

[Browse Discourse integration templates](https://n8n.io/integrations/discourse/), or [search all templates](https://n8n.io/workflows/)

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

# TheHive 5 credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/thehive5.md "Edit this page")

# TheHive 5 credentials#

You can use these credentials to authenticate the following nodes with TheHive 5.

  * [TheHive 5](../../app-nodes/n8n-nodes-base.thehive5/)



TheHive and TheHive 5

n8n provides two nodes for TheHive. Use these credentials with TheHive 5 node. If you're using TheHive node for TheHive 3 or TheHive 4, use [TheHive credentials](../thehive/).

## Prerequisites#

Install [TheHive 5](https://docs.strangebee.com/thehive/download/) on your server.

## Supported authentication methods#

  * API key



## Related resources#

Refer to [TheHive's API documentation](https://docs.strangebee.com/thehive/api-docs/) for more information about the service.

## Using API key#

To configure this credential, you'll need:

  * An **API Key** : Users with `orgAdmin` and `superAdmin` accounts can generate API keys:
    * `orgAdmin` account: Go to **Organization > Create API Key** for the user you wish to generate a key for.
    * `superAdmin` account: Go to **Users > Create API Key** for the user you wish to generate a key for.
    * Refer to [API Authentication](https://docs.strangebee.com/cortex/api/api-guide/?h=api+key#authentication) for more information.
  * A **URL** : The URL of your TheHive server.
  * **Ignore SSL Issues** : When turned on, n8n will connect even if SSL certificate validation fails.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

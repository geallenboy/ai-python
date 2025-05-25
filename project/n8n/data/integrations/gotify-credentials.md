# Gotify credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/gotify.md "Edit this page")

# Gotify credentials#

You can use these credentials to authenticate the following nodes:

  * [Gotify](../../app-nodes/n8n-nodes-base.gotify/)



## Prerequisites#

Install [Gotify](https://gotify.net/docs/install) on your server.

## Supported authentication methods#

  * API token



## Related resources#

Refer to [Gotify's API documentation](https://gotify.net/api-docs) for more information about the service.

## Using API token#

To configure this credential, you'll need:

  * An **App API Token** : Only required if you'll use this credential to create messages. To generate an App API token, create an application from the **Apps** menu. Refer to [Gotify's Push messages documentation](https://gotify.net/docs/pushmsg) for more information.
  * A **Client API Token** : Required for all actions other than creating messages (such as deleting or retrieving messages). To generate a Client API token, create a client from the **Clients** menu.
  * The **URL** of the Gotify host

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

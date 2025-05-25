# Raindrop credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/raindrop.md "Edit this page")

# Raindrop credentials#

You can use these credentials to authenticate the following nodes:

  * [Raindrop](../../app-nodes/n8n-nodes-base.raindrop/)



## Prerequisites#

Create a [Raindrop](https://raindrop.io/) account.

## Supported authentication methods#

  * OAuth2



## Related resources#

Refer to [Raindrop's API documentation](https://developer.raindrop.io/) for more information about the service.

## Using OAuth#

To configure this credential, you'll need:

  * A **Client ID**
  * A **Client Secret**



Generate both by creating a Raindrop app.

To create an app, go to **Settings >** [**Integrations**](https://app.raindrop.io/settings/integrations) and select **\+ Create new app** in the **For Developers** section.

Use these settings for your app:

  * Copy the **OAuth Redirect URL** from n8n and add it as a **Redirect URI** in your app.
  * Copy the **Client ID** and **Client Secret** from the Raindrop app and enter them in your n8n credential.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

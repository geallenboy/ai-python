# Xero credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/xero.md "Edit this page")

# Xero credentials#

You can use these credentials to authenticate the following nodes:

  * [Xero](../../app-nodes/n8n-nodes-base.xero/)



## Prerequisites#

Create a [Xero](https://www.xero.com/) account.

## Supported authentication methods#

  * OAuth2



## Related resources#

Refer to [Zero's API documentation](https://developer.xero.com/documentation/api/accounting/overview) for more information about the service.

## Using OAuth2#

To configure this credential, you'll need:

  * A **Client ID** : Generated when you create a new app for a custom connection.
  * A **Client Secret** : Generated when you create a new app for a custom connection.



To generate your Client ID and Client Secret, [create an OAuth2 custom connection app](https://developer.xero.com/documentation/guides/oauth2/custom-connections/) in your Xero developer portal [**My Apps**](https://developer.xero.com/app/manage).

Use these settings for your app:

Xero App Name

Xero doesn't support app instances within the Xero Developer Centre that contain `n8n` in their name.

  * Select **Web app** as the **Integration Type**.
  * For the **Company or Application URL** , enter the URL of your n8n server or reverse proxy address. For cloud users, for example, this is: `https://your-username.app.n8n.cloud/`.
  * Copy the **OAuth Redirect URL** from n8n and add it as an **OAuth 2.0 redirect URI** in your app.
  * Select appropriate **scopes** for your app. Refer to [OAuth2 Scopes](https://developer.xero.com/documentation/guides/oauth2/scopes/) for more information.
    * To use all functionality in the [Xero](../../app-nodes/n8n-nodes-base.xero/) node, add the `accounting.contacts` and `accounting.transactions` scopes.



Refer to Xero's [OAuth Custom Connections](https://developer.xero.com/documentation/guides/oauth2/custom-connections) documentation for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

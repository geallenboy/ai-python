# Pushbullet credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/pushbullet.md "Edit this page")

# Pushbullet credentials#

You can use these credentials to authenticate the following nodes:

  * [Pushbullet](../../app-nodes/n8n-nodes-base.pushbullet/)



## Prerequisites#

Create a [Pushbullet](https://www.pushbullet.com/) account.

## Supported authentication methods#

  * OAuth2



## Related resources#

Refer to [Pushbullet's API documentation](https://docs.pushbullet.com/) for more information about the service.

## Using OAuth2#

To configure this credential, you'll need:

  * A **Client ID** : Generated when you create a Pushbullet app, also known as an OAuth client.
  * A **Client Secret** : Generated when you create a Pushbullet app, also known as an OAuth client.



To generate the **Client ID** and **Client Secret** , go to the [create client](https://www.pushbullet.com/create-client) page. Copy the **OAuth Redirect URL** from n8n and add this as your **redirect_uri** for the app/client. Use the **client_id** and **client_secret** from the OAuth Client in your n8n credential.

Refer to Pushbullet's [OAuth2 Guide](https://docs.pushbullet.com/#oauth2) for more information.

Pushbullet OAuth test link

Pushbullet offers a test link during the client creation process described above. This link isn't compatible with n8n. To verify the authentication works, use the **Connect my account** button in n8n.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

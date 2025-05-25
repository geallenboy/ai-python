# Philips Hue credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/philipshue.md "Edit this page")

# Philips Hue credentials#

You can use these credentials to authenticate the following nodes:

  * [Philips Hue](../../app-nodes/n8n-nodes-base.philipshue/)



## Prerequisites#

Create a [Philips Hue](https://www.philips-hue.com/en-us) account.

## Supported authentication methods#

  * OAuth2



## Related resources#

Refer to [Philips Hue's CLIP API documentation](https://developers.meethue.com/develop/hue-api-v2/api-reference/) for more information about the service.

## Using OAuth2#

Note for n8n Cloud users

Cloud users don't need to provide connection details. Select **Connect my account** to connect through your browser.

If you're using the built-in OAuth connection, you don't need to enter an **APP ID**.

If you need to configure OAuth2 from scratch, you'll need a [Philips Hue developer](https://developers.meethue.com/) account

Create a new remote app on the [Add new Hue Remote API app](https://developers.meethue.com/add-new-hue-remote-api-app/) page.

Use these settings for your app:

  * Copy the **OAuth Callback URL** from n8n and add it as a **Callback URL**.
  * Copy the **AppId** , **ClientId** , and **ClientSecret** and enter these in the corresponding fields in n8n.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

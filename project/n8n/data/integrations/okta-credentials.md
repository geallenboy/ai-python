# Okta credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/okta.md "Edit this page")

# Okta credentials#

You can use these credentials to authenticate the following nodes:

  * [Okta](../../app-nodes/n8n-nodes-base.okta/)



## Prerequisites#

Create an [Okta free trial](https://www.okta.com/free-trial/) or create an admin account on an existing Okta org.

## Supported authentication methods#

  * SSWS API Access token



## Related resources#

Refer to [Okta's documentation](https://developer.okta.com/docs/reference/) for more information about the service.

## Using SSWS API access token#

To configure this credential, you'll need:

  * The **URL** : The base URL of your Okta org, also referred to as your unique subdomain. There are two quick ways to access it:
    1. In the Admin Console, select your **Profile** , hover over the domain listed below your username, and select the **Copy** icon. Paste this into n8n, but be sure to add `https://` before it.
    2. Copy the base URL of your Admin Console URL, for example `https://dev-123456-admin.okta.com`. Paste it into n8n and remove `-admin`, for example: `https://dev-123456.okta.com`.
  * An **SSWS Access Token** : Create a token by going to **Security > API > Tokens > Create token**. Refer to [Create Okta API tokens](https://help.okta.com/en-us/content/topics/security/api.htm?cshid=ext-create-api-token#create-okta-api-token) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

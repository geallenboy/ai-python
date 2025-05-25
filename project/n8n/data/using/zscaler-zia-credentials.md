# Zscaler ZIA credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/zscalerzia.md "Edit this page")

# Zscaler ZIA credentials#

You can use these credentials to authenticate when using the [HTTP Request node](../../core-nodes/n8n-nodes-base.httprequest/) to make a [Custom API call](../../../custom-operations/).

## Prerequisites#

Create an admin account on a [Zscaler Internet Access (ZIA)](https://www.zscaler.com/products/zscaler-internet-access) cloud instance.

## Supported authentication methods#

  * Basic auth and API key combo



## Related resources#

Refer to [Zscaler ZIA's documentation](https://help.zscaler.com/zia/getting-started-zia-api) for more information about the service.

This is a credential-only node. Refer to [Custom API operations](../../../custom-operations/) to learn more. View [example workflows and related content](https://n8n.io/integrations/zscaler-zia/) on n8n's website.

## Using basic auth and API key combo#

To configure this credential, you'll need:

  * A **Base URL** : Enter the base URL of your Zscaler ZIA cloud name. To get your base URL, log in to the ZIA Admin Portal and go to **Administration > Cloud Service API Security**. The base URL is displayed in both the **Cloud Service API Key** tab and the **OAuth 2.0 Authorization Servers** tab.
  * A **Username** : Enter your ZIA admin username.
  * A **Password** : Enter your ZIA admin password.
  * An **Api Key** : Get an API key by creating one from **Administration > Cloud Service API Security > Cloud Service API Key**.



Refer to [About Cloud Service API Key](https://help.zscaler.com/zia/about-cloud-service-api-key) for more detailed instructions.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

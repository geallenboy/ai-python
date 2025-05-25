# Cisco Secure Endpoint credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/ciscosecureendpoint.md "Edit this page")

# Cisco Secure Endpoint credentials#

You can use these credentials to authenticate when using the [HTTP Request node](../../core-nodes/n8n-nodes-base.httprequest/) to make a [Custom API call](../../../custom-operations/).

## Prerequisites#

  * Create a [Cisco DevNet developer account](https://developer.cisco.com).
  * Access to a [Cisco Secure Endpoint license](https://www.cisco.com/site/us/en/products/security/endpoint-security/secure-endpoint/index.html).



## Authentication methods#

  * OAuth2



## Related resources#

Refer to [Cisco Secure Endpoint's documentation](https://developer.cisco.com/docs/secure-endpoint/introduction/) for more information about the service.

This is a credential-only node. Refer to [Custom API operations](../../../custom-operations/) to learn more. View [example workflows and related content](https://n8n.io/integrations/cisco-secure-endpoint/) on n8n's website.

## Using OAuth2#

To configure this credential, you'll need:

  * The **Region** for your Cisco Secure Endpoint. Options are:
    * Asia Pacific, Japan, and China
    * Europe
    * North America
  * A **Client ID** : Provided when you register a SecureX API Client
  * A **Client Secret** : Provided when you register a SecureX API Client



To get a Client ID and Client Secret, you'll need to Register a SecureX API Client. Refer to [Cisco Secure Endpoint's authentication documentation](https://developer.cisco.com/docs/secure-endpoint/authentication/#authentication) for detailed instructions. Use the SecureX **Client Password** as the **Client Secret** within the n8n credential.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

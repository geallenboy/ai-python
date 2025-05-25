# Venafi TLS Protect Datacenter credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/venafitlsprotectdatacenter.md "Edit this page")

# Venafi TLS Protect Datacenter credentials#

You can use these credentials to authenticate the following nodes:

  * [Venafi TLS Protect Datacenter node](../../app-nodes/n8n-nodes-base.venafitlsprotectdatacenter/)



## Prerequisites#

  * Create a Venafi [TLS Protect Datacenter](https://venafi.com/) account.
  * Set the expiration and refresh time for tokens. Refer to [Setting up token authentication](https://docs.venafi.com/Docs/current/TopNav/Content/SDK/AuthSDK/t-SDKa-Setup-OAuth.php) for more information.
  * Create an [API integration](https://docs.venafi.com/Docs/current/TopNav/Content/API-ApplicationIntegration/c-APIAppIntegrations-about.php) in **API > Integrations**. Refer to [Integrating other systems with Venafi products](https://docs.venafi.com/Docs/current/TopNav/Content/API-ApplicationIntegration/t-APIAppIntegrations-creating.php) for detailed instructions.
    * Take note of the Client ID for your integration.
    * Choose the scopes needed for the operations you want to perform within n8n. Refer to the scopes table in [Integrating other systems with Venafi products](https://docs.venafi.com/Docs/current/TopNav/Content/API-ApplicationIntegration/t-APIAppIntegrations-creating.php) for more details on available scopes.



## Supported authentication methods#

  * API integration



## Related resources#

Refer to [Venafi's API integration documentation](https://docs.venafi.com/Docs/currentSDK/TopNav/Content/SDK/WebSDK/c-sdk-AboutThisGuide.php) for more information about the service.

## Using API integration#

To configure this credential, you'll need:

  * A **Domain** : Enter your Venafi TLS Protect Datacenter domain.
  * A **Client ID** : Enter the **Client ID** from your API integration. Refer to the information and links in Prerequisites for more information on creating an API integration.
  * A **Username** : Enter your username.
  * A **Password** : Enter your password.
  * **Allow Self-Signed Certificates** : If turned on, the credential will allow self-signed certificates.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

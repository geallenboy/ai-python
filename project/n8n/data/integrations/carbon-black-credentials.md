# Carbon Black credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/carbonblack.md "Edit this page")

# Carbon Black credentials#

You can use these credentials to authenticate when using the [HTTP Request node](../../core-nodes/n8n-nodes-base.httprequest/) to make a [Custom API call](../../../custom-operations/).

## Prerequisites#

  * Create a [Carbon Black subscription](https://www.vmware.com/products/carbon-black-cloud.html).
  * Create a [Carbon Black developer account](https://developer.carbonblack.com/).



## Authentication methods#

  * API key



## Related resources#

Refer to [Carbon Black's documentation](https://developer.carbonblack.com/reference/carbon-black-cloud/cb-defense/latest/rest-api/) for more information about the service.

This is a credential-only node. Refer to [Custom API operations](../../../custom-operations/) to learn more. View [example workflows and related content](https://n8n.io/integrations/carbon-black/) on n8n's website.

## Using API key#

To configure this credential, you'll need:

  * A **URL** : This URL is determined by the environment/product URL you use. You can find it by looking at the web address of your Carbon Black Cloud console. Refer to [Carbon Black's URL Parts documentation](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication#the-url-parts) for more information.
  * An **Access Token** : Refer to the [Carbon Black Create an API key documentation](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication#carbon-black-cloud-manages-identities-and-roles) to create an API key. Add the **API Secret Key** as the **Access Token** in n8n.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

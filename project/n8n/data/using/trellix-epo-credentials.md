# Trellix ePO credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/trellixepo.md "Edit this page")

# Trellix ePO credentials#

You can use these credentials to authenticate when using the [HTTP Request node](../../core-nodes/n8n-nodes-base.httprequest/) to make a [Custom API call](../../../custom-operations/).

## Prerequisites#

Create a [Trellix ePolicy Orchestrator](https://www.trellix.com/products/epo/) account.

## Supported authentication methods#

  * Basic auth



## Related resources#

Refer to [Trellix ePO's documentation](https://docs.trellix.com/bundle/epolicy-orchestrator-web-api-reference-guide/page/GUID-D87A6839-AED2-47B0-BE93-5BF83F710278.html) for more information about the service.

This is a credential-only node. Refer to [Custom API operations](../../../custom-operations/) to learn more. View [example workflows and related content](https://n8n.io/integrations/trellix-epo/) on n8n's website.

## Using basic auth#

To configure this credential, you'll need:

  * A **Username** to connect as.
  * A **Password** for that user account.



n8n uses These fields to build the `-u` parameter in the format of `-u username:pw`. Refer to [Web API basics](https://docs.trellix.com/bundle/epolicy-orchestrator-web-api-reference-guide/page/GUID-2503B69D-2BCE-4491-9969-041838B39C1F.html) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

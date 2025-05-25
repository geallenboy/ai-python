# Azure OpenAI credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/azureopenai.md "Edit this page")

# Azure OpenAI credentials#

You can use these credentials to authenticate the following nodes:

  * [Chat Azure OpenAI](../../cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatazureopenai/)
  * [Embeddings Azure OpenAI](../../cluster-nodes/sub-nodes/n8n-nodes-langchain.embeddingsazureopenai/)



## Prerequisites#

  * Create an [Azure](https://azure.microsoft.com) subscription.
  * Access to Azure OpenAI within that subscription. You may need to [request access](https://aka.ms/oai/access) if your organization doesn't yet have it.



## Supported authentication methods#

  * API key



## Related resources#

Refer to [Azure OpenAI's API documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference) for more information about the service.

## Using API key#

To configure this credential, you'll need:

  * A **Resource Name** : the **Name** you give the resource
  * An **API key** : **Key 1** works well. This can be accessed before deployment in **Keys and Endpoint**.
  * The **API Version** the credentials should use. See the [Azure OpenAI API preview lifecycle documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/api-version-deprecation) for more information about API versioning in Azure OpenAI.



To get the information above, [create and deploy an Azure OpenAI Service resource](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource).

Model name for Azure OpenAI nodes

Once you deploy the resource, use the **Deployment name** as the model name for the Azure OpenAI nodes where you're using this credential.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

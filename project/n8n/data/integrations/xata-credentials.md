# Xata credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/xata.md "Edit this page")

# Xata credentials#

You can use these credentials to authenticate the following nodes:

  * [Xata](../../cluster-nodes/sub-nodes/n8n-nodes-langchain.memoryxata/)



## Prerequisites#

Create a [Xata](https://xata.io/) database or an account on an existing database.

## Supported authentication methods#

  * API key



## Related resources#

Refer to [Xata's documentation](https://xata.io/docs/rest-api/authentication) for more information about the service.

View n8n's [Advanced AI](../../../../advanced-ai/) documentation.

## Using API key#

To configure this credential, you'll need:

  * The **Database Endpoint** : The Workspace API requires that you identify the database you're requesting information from using this format: `https://{workspace-display-name}-{workspace-id}.{region}.xata.sh/db/{dbname}`. Refer to [Workspace API](https://xata.io/docs/rest-api#workspace-api) for more information.
    * `{workspace-display-name}`: The workspace display name is an optional identifier you can include in your Database Endpoint. The API ignores it, but including it can make it easier to figure out which workspace this database is in if you're saving multiple credentials.
    * `{workspace-id}`: The unique ID of the workspace, 6 alphanumeric characters.
    * `{region}`: The hosting region for the database. This value must match the database region configuration.
    * `{dbname}`: The name of the database you're interacting with.
  * A **Branch** : Enter the name of the GitHub branch for your database.
  * An **API Key** : To generate an API key, go to [**Account Settings**](https://app.xata.io/settings) and select **\+ Add a key**. Refer to [Generate an API Key](https://xata.io/docs/rest-api#generate-an-api-key) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

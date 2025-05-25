# Linear credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/linear.md "Edit this page")

# Linear credentials#

You can use these credentials to authenticate the following nodes:

  * [Linear Trigger](../../trigger-nodes/n8n-nodes-base.lineartrigger/)
  * [Linear](../../app-nodes/n8n-nodes-base.linear/)



## Prerequisites#

Create a [Linear](https://linear.app/) account.

## Supported authentication methods#

  * API key
  * OAuth2



## Related resources#

Refer to [Linear's API documentation](https://developers.linear.app/docs/graphql/working-with-the-graphql-api) for more information about the service.

## Using API key#

To configure this credential, you'll need:

  * A personal **API Key** : Create an API key in your [**Settings > API**](https://linear.app/n8n/settings/api). Refer to the [Linear Personal API keys documentation](https://developers.linear.app/docs/graphql/working-with-the-graphql-api#personal-api-keys) for more information.



## Using OAuth2#

To configure this credential, you'll need:

  * A **Client ID** : Generated when you create a new OAuth2 application.
  * A **Client Secret** : Generated when you create a new OAuth2 application.
  * Select the **Actor** : The actor defines how the OAuth2 application should create issues, comments and other changes. Options include:
    * **User** (Linear's default): The application creates resources as the authorizing user. Use this option if you want each user to do their own authentication.
    * **Application** : The application creates resources as itself. Use this option if you have only one user (like an admin) authorizing the application.
  * To use this credential with the [Linear Trigger](../../trigger-nodes/n8n-nodes-base.lineartrigger/) node, you must enable the **Include Admin Scope** toggle.



Refer to the [Linear OAuth2 Authentication documentation](https://developers.linear.app/docs/oauth/authentication) for more detailed instructions and explanations. Use the n8n **OAuth Redirect URL** as the **Redirect callback URL** in your Linear OAuth2 application.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

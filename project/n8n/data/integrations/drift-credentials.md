# Drift credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/drift.md "Edit this page")

# Drift credentials#

You can use these credentials to authenticate the following nodes:

  * [Drift](../../app-nodes/n8n-nodes-base.drift/)



## Prerequisites#

  * Create a [Drift](https://www.drift.com/) account.
  * [Create a Drift app](https://devdocs.drift.com/docs/quick-start#3-install-it-to-your-drift-account-).



## Supported authentication methods#

  * API personal access token
  * OAuth2



## Related resources#

Refer to [Drift's API documentation](https://devdocs.drift.com/docs/using-drift-apis) for more information about the service.

## Using API personal access token#

To configure this credential, you'll need:

  * A **Personal Access Token** : To get a token, [create a Drift app](https://devdocs.drift.com/docs/quick-start#3-install-it-to-your-drift-account-). [Install the app](https://devdocs.drift.com/docs/quick-start#3-install-it-to-your-drift-account-) to generate an OAuth Access token. Add this to the n8n credential as your **Personal Access Token**.



## Using OAuth2#

Note for n8n Cloud users

Cloud users don't need to provide connection details. Select **Connect my account** to connect through your browser.

If you need to configure OAuth2 from scratch or need more detail on what's happening in the OAuth web flow, refer to the instructions in the [Drift Authentication and Scopes documentation](https://devdocs.drift.com/docs/authentication-and-scopes) to set up OAuth for your app.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

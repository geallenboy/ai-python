# Bitbucket credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/bitbucket.md "Edit this page")

# Bitbucket credentials#

You can use these credentials to authenticate the following nodes:

  * [Bitbucket Trigger](../../trigger-nodes/n8n-nodes-base.bitbuckettrigger/)



## Prerequisites#

Create a [Bitbucket](https://www.bitbucket.com/) account.

## Supported authentication methods#

  * API username and app password



## Related resources#

Refer to [Bitbucket's API documentation](https://developer.atlassian.com/cloud/bitbucket/rest/intro/#authentication) for more information about the service.

## Using API username/app password#

To configure this credential, you'll need:

  * A **Username** : Visible in your Bitbucket profile settings **Personal settings > Account settings**.
  * An **App Password** : Refer to the Bitbucket instructions to [Create an app password](https://support.atlassian.com/bitbucket-cloud/docs/create-an-app-password/).



## App password permissions#

Bitbucket API credentials will only work if the user account you generated the app password for has the appropriate privilege scopes for the selected app password permissions. The n8n credentials dialog will throw an error if the user account lacks the appropriate permissions for the selected scope, like `Your credentials lack one or more required privilege scopes`.

See the [Bitbucket App password permissions documentation](https://support.atlassian.com/bitbucket-cloud/docs/app-password-permissions/) for more information on working with these permissions.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

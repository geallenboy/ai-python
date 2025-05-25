# Storyblok credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/storyblok.md "Edit this page")

# Storyblok credentials#

You can use these credentials to authenticate the following nodes:

  * [Storyblok](../../app-nodes/n8n-nodes-base.storyblok/)



## Prerequisites#

Create a [Storyblok](https://www.storyblok.com/) account.

## Supported authentication methods#

  * Content API key: For read-only access
  * Management API key: For full CRUD operations



Content API support

n8n supports Content API v1 only.

## Related resources#

Refer to Storyblok's [Content v1 API documentation](https://www.storyblok.com/docs/api/content-delivery/v1) and [Management API documentation](https://www.storyblok.com/docs/api/management/getting-started/introduction) for more information about the services.

## Using Content API key#

To configure this credential, you'll need:

  * A Content **API Key** : Go to your Storyblok workspace's **Settings > Access Tokens** to get an API key. Choose an **Access Level** of either **Public** (`version=published`) or **Preview** (`version-published` and `version=draft`). Enter this access token as your **API Key**. Refer to [How to retrieve and generate access tokens](https://www.storyblok.com/faq/retrieve-and-generate-access-tokens) for more detailed instructions.



Refer to [Content v1 API Authentication](https://www.storyblok.com/docs/api/content-delivery/v1#topics/authentication) for more information about supported operations with each Access Level.

## Using Management API key#

To configure this credential, you'll need:

  * A **Personal Access Token** : Go to [**My Account**](https://app.storyblok.com/#!/me/account) **> Personal access tokens** to generate a new access token. Enter this access token as your **Personal Access Token**.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

# Jenkins credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/jenkins.md "Edit this page")

# Jenkins credentials#

You can use these credentials to authenticate the following nodes:

  * [Jenkins](../../app-nodes/n8n-nodes-base.jenkins/)



## Prerequisites#

Create an account on a [Jenkins](https://www.jenkins.io/) instance.

## Supported authentication methods#

  * API token



## Related resources#

Jenkins doesn't provide public API documentation; API documentation for each page is available from the user interface in the bottom right. Refer to those detailed pages for more information about the service. Refer to [Jenkins Remote Access API](https://www.jenkins.io/doc/book/using/remote-access-api/) for information on the API and API wrappers.

## Using API token#

To configure this credential, you'll need:

  * The **Jenkins Username** : For the user whom the token belongs to
  * A **Personal API Token** : Generate this from the user's **profile details > Configure > Add new token**. Refer to [these Stack Overflow instructions](https://stackoverflow.com/questions/45466090/how-to-get-the-api-token-for-jenkins) for more detail.
  * The **Jenkins Instance URL**



Jenkins rebuilt their API token setup in 2018. If you're working with an older Jenkins instance, be sure you're using a non-legacy API token. Refer to [Security Hardening: New API token system in Jenkins 2.129+](https://www.jenkins.io/blog/2018/07/02/new-api-token-system/) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

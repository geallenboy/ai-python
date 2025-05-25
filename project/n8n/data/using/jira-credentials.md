# Jira credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/jira.md "Edit this page")

# Jira credentials#

You can use these credentials to authenticate the following nodes:

  * [Jira](../../app-nodes/n8n-nodes-base.jira/)
  * [Jira Trigger](../../trigger-nodes/n8n-nodes-base.jiratrigger/)



## Prerequisites#

Create a [Jira](https://www.atlassian.com/software/jira) Software Cloud or Server account.

## Supported authentication methods#

  * SW Cloud API token: Use this method with [Jira Software Cloud](https://www.atlassian.com/software/jira).
  * SW Server account: Use this method with [Jira Software Server](https://www.atlassian.com/software/jira/download.).



## Related resources#

Refer to [Jira's API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/#about) for more information about the service.

## Using SW Cloud API token#

To configure this credential, you'll need an account on [Jira Software Cloud](https://www.atlassian.com/software/jira).

Then:

  1. Log in to your Atlassian profile > **Security > API tokens** page, or jump straight there using this [link](https://id.atlassian.com/manage-profile/security/api-tokens).
  2. Select **Create API Token**.
  3. Enter a good **Label** for your token, like `n8n integration`.
  4. Select **Create**.
  5. Copy the API token.
  6. In n8n, enter the **Email** address associated with your Jira account.
  7. Paste the API token you copied as your **API Token**.
  8. Enter the **Domain** you access Jira on, for example `https://example.atlassian.net`.



Refer to [Manage API tokens for your Atlassian account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) for more information.

New tokens

New tokens may take up to a minute before they work. If your credential verification fails the first time, wait a minute before retrying.

## Using SW Server account#

To configure this credential, you'll need an account on [Jira Software Server](https://www.atlassian.com/software/jira/download.).

Then:

  1. Enter the **Email** address associated with your Jira account.
  2. Enter your Jira account **Password**.
  3. Enter the **Domain** you access Jira on.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

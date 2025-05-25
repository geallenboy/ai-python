# Trello credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/trello.md "Edit this page")

# Trello credentials#

You can use these credentials to authenticate the following nodes:

  * [Trello](../../app-nodes/n8n-nodes-base.trello/)
  * [Trello Trigger](../../trigger-nodes/n8n-nodes-base.trellotrigger/)



## Supported authentication methods#

  * API key



## Related resources#

Refer to [Trello's API documentation](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/) for more information about the service.

## Using API key#

To configure this credential, you'll need a [Trello](https://trello.com/) account and:

  * An **API Key**
  * An **API Token**



To generate both the API Key and API Token, create a Trello Power-Up:

  1. Open the Trello [Power-Up Admin Portal](https://trello.com/power-ups/admin).
  2. Select **New**.
  3. Enter a **Name** for your Power-Up, like `n8n integration`.
  4. Select the **Workspace** the Power-Up should have access to.
  5. Leave the **iframe connector URL** blank.
  6. Enter appropriate contact information.
  7. Select **Create**.
  8. This should open the Power-Up to the **API Key** page. (If it doesn't, open that page.)
  9. Select **Generate a new API Key**.
  10. Copy the **API key** from Trello and enter it in your n8n credential.
  11. In your Trello API key page, enter your n8n base URL as an **Allowed origin**.
  12. In **Capabilities** make sure to select the necessary options.
  13. Select the **Token** link next to your Trello **API Key**.
  14. When prompted, select **Allow** to grant all the permissions asked for.
  15. Copy the Trello **Token** and enter it as the n8n **API Token**.



Refer to Trello's [API Introduction](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/#api-introduction) for more information on API keys and tokens. Refer to Trello's [Power-Up Admin Portal](https://developer.atlassian.com/cloud/trello/guides/power-ups/managing-power-ups/#power-up-admin-portal) for more information on creating Power-Ups.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

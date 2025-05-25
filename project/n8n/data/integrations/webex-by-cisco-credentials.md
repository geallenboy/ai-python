# Webex by Cisco credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/ciscowebex.md "Edit this page")

# Webex by Cisco credentials#

You can use these credentials to authenticate the following nodes:

  * [Webex by Cisco](../../app-nodes/n8n-nodes-base.ciscowebex/)
  * [Webex by Cisco Trigger](../../trigger-nodes/n8n-nodes-base.ciscowebextrigger/)



## Prerequisites#

Create a [Webex by Cisco](https://www.webex.com/) account (this should automatically get you [developer account access](https://developer.webex.com)).

## Supported authentication methods#

  * OAuth2



## Related resources#

Refer to [Webex's API documentation](https://developer.webex.com/docs/getting-started) for more information about the service.

## Using OAuth2#

Note for n8n Cloud users

You'll only need to enter the Credentials Name and select the **Connect my account** button in the OAuth credential to connect your Webex by Cisco account to n8n.

Should you need to configure OAuth2 from scratch, you'll need to create an integration to use this credential. Refer to the instructions in the [Webex Registering your Integration documentation](https://developer.webex.com/docs/integrations#registering-your-integration) to begin.

n8n recommends using the following **Scopes** for your integration:

  * `spark:rooms_read`
  * `spark:messages_write`
  * `spark:messages_read`
  * `spark:memberships_read`
  * `spark:memberships_write`
  * `meeting:recordings_write`
  * `meeting:recordings_read`
  * `meeting:preferences_read`
  * `meeting:schedules_write`
  * `meeting:schedules_read`

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

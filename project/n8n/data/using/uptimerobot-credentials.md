# UptimeRobot credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/uptimerobot.md "Edit this page")

# UptimeRobot credentials#

You can use these credentials to authenticate the following nodes:

  * [UptimeRobot](../../app-nodes/n8n-nodes-base.uptimerobot/)



## Prerequisites#

Create an [UptimeRobot](https://uptimerobot.com/) account.

## Supported authentication methods#

  * API key



## Related resources#

Refer to [UptimeRobot's API documentation](https://uptimerobot.com/api/) for more information about the service.

## Using API key#

To configure this credential, you'll need:

  * An **API Key** : Get your API Key from **My Settings > API Settings**. Create a **Main API Key** and enter this key in your n8n credential.



### API key types#

UptimeRobot supports three API key types:

  * **Account-specific** (also known as **main**): Pulls data for multiple monitors.
  * **Monitor-specific** : Pulls data for a single monitor.
  * **Read-only** : Only runs `GET` API calls.



To complete all of the operations in the UptimeRobot node, use the **Main** or **Account-specific** API key type. Refer to [API authentication](https://uptimerobot.com/api/#auth) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

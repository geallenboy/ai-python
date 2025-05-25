# MSG91 credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/msg91.md "Edit this page")

# MSG91 credentials#

You can use these credentials to authenticate the following nodes:

  * [MSG91](../../app-nodes/n8n-nodes-base.msg91/)



## Prerequisites#

Create a [MSG91](https://msg91.com/) account.

## Supported authentication methods#

  * API key



## Related resources#

Refer to [MSG91's API documentation](https://docs.msg91.com/overview) for more information about the service.

## Using API key#

To configure this credential, you'll need:

  * An **Authentication Key** : To get your Authentication Key, go to the user menu and select **Authkey**. Refer to MSG91's [Where can I find my authentication key? documentation](https://msg91.com/help/where-can-i-find-my-authentication-key) for more information.



## IP Security#

MSG91 enables [IP Security](https://msg91.com/help/what-do-you-mean-by-api-security) by default for authkeys.

For the n8n credentials to function with this setting enabled, add all the [n8n IP addresses](../../../../manage-cloud/cloud-ip/) as whitelisted IPs in MSG91. You can add them in one of two places, depending on your desired security level:

  * To allow any/all authkeys in the account to work with n8n, add the n8n IP addresses in the **Company's whitelisted IPs** section of the **Authkey** page.
  * To allow only specific authkeys to work with n8n, add the n8n IP addresses in the **Whitelisted IPs** section of an authkey's details.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

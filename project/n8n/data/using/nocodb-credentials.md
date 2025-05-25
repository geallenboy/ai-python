# NocoDB credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/nocodb.md "Edit this page")

# NocoDB credentials#

You can use these credentials to authenticate the following nodes:

  * [NocoDB](../../app-nodes/n8n-nodes-base.nocodb/)



## Supported authentication methods#

  * API token (recommended)
  * User auth token

User auth token deprecation

NocoDB deprecated user auth tokens in v0.205.1. Use API tokens instead.




## Related resources#

Refer to [NocoDB's API documentation](https://data-apis-v2.nocodb.com/) for more information about the service.

## Using API token#

To configure this credential, you'll need a [NocoDB](https://www.nocodb.com/) instance and:

  * An **API Token**
  * Your database **Host**



To generate an API token:

  1. Log into NocoDB and select the **User menu** in the bottom left sidebar.
  2. Select **Account Settings**.
  3. Open the **Tokens** tab.
  4. Select **Add new API token**.
  5. Enter a **Name** for your token, like `n8n integration`.
  6. Select **Save**.
  7. Copy the **API Token** and enter it in your n8n credential.
  8. Enter the **Host** of your NocoDB instance in your n8n credential, for example `http://localhost:8080`.



Refer to the NocoDB [API Tokens documentation](https://docs.nocodb.com/account-settings/api-tokens/) for more detailed instructions.

## Using user auth token#

Before NocoDB deprecated it, user auth token was a temporary token designed for quick experiments with the API, valid for a session until the user logs out or for 10 hours.

User auth token deprecation

NocoDB deprecated user auth tokens in v0.205.1. Use API tokens instead.

To configure this credential, you'll need a [NocoDB](https://www.nocodb.com/) instance and:

  * A **User Token**
  * Your database **Host**



To generate a user auth token:

  1. Log into NocoDB and select the **User menu** in the bottom left sidebar.
  2. Select **Copy Auth token**.
  3. Enter that auth token as the **User Token** in n8n. 
  4. Enter the **Host** of your NocoDB instance, for example `http://localhost:8080`.



Refer to the NocoDB [Auth Tokens documentation](https://docs.nocodb.com/account-settings/api-tokens/#auth-tokens) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

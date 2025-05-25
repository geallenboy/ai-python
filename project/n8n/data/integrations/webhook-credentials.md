# Webhook credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/webhook.md "Edit this page")

# Webhook credentials#

You can use these credentials to authenticate the following nodes:

  * [Webhook](../../core-nodes/n8n-nodes-base.webhook/)



## Prerequisites#

You must use the authentication method required by the app or service you want to query.

## Supported authentication methods#

  * Basic auth
  * Header auth
  * JWT auth
  * None



## Using basic auth#

Use this generic authentication if your app or service supports basic authentication.

To configure this credential, enter:

  * The **Username** you use to access the app or service your HTTP Request is targeting
  * The **Password** that goes with that username



## Using header auth#

Use this generic authentication if your app or service supports header authentication.

To configure this credential, enter:

  * The header **Name** you need to pass to the app or service your HTTP request is targeting
  * The **Value** for the header 



Read more about [HTTP headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#authentication)

## Using JWT auth#

[**JWT Auth**](https://jwt.io/introduction/) is a method of authentication that uses JSON Web Tokens (JWT) to digitally sign data. This authentication method uses the **JWT credential** and can use either a **Passphrase** or **PEM Key** as key type. Refer to [JWT credential](../jwt/) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

# Paddle credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/paddle.md "Edit this page")

# Paddle credentials#

You can use these credentials to authenticate the following nodes:

  * [Paddle](../../app-nodes/n8n-nodes-base.paddle/)



## Prerequisites#

Create a [Paddle](https://paddle.com/) account.

## Supported authentication methods#

  * API access token (Classic)



Paddle Classic API

This credential works with Paddle Classic's API. If you joined Paddle after August 2023, you're using the [Paddle Billing API](https://developer.paddle.com/api-reference/overview) and this credential may not work for you.

## Related resources#

Refer to [Paddle Classic's API documentation](https://developer.paddle.com/classic/api-reference/1384a288aca7a-api-reference) for more information about the service.

## Using API access token (Classic)#

To configure this credential, you'll need:

  * A **Vendor Auth Code** : Created when you generate an API key.
  * A **Vendor ID** : Displayed when you generate an API key.
  * **Use Sandbox Environment API** : When turned on, nodes using this credential will hit the Sandbox API endpoint instead of the live API endpoint.



To generate an auth code and view your Vendor ID, go to **Paddle > Developer Tools > Authentication > Generate Auth Code**. Select **Reveal Auth Code** to display the Auth Code. Refer to [API Authentication](https://developer.paddle.com/classic/api-reference/zg9joji1mzuzotg5-api-authentication) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

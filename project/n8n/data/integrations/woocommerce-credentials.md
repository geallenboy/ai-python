# WooCommerce credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/woocommerce.md "Edit this page")

# WooCommerce credentials#

You can use these credentials to authenticate the following nodes:

  * [WooCommerce](../../app-nodes/n8n-nodes-base.woocommerce/)
  * [WooCommerce Trigger](../../trigger-nodes/n8n-nodes-base.woocommercetrigger/)



## Prerequisites#

  * Install the [WooCommerce](https://woocommerce.com/) plugin on your WordPress website.
  * In WordPress, go to **Settings > Permalinks** and set your WordPress permalinks to use something other than **Plain**.



## Supported authentication methods#

  * API key



## Related resources#

Refer to [WooCommerce's REST API documentation](https://developer.woocommerce.com/docs/getting-started-with-the-woocommerce-rest-api/) for more information about the service.

## Using API key#

To configure this credential, you'll need:

  * A **Consumer Key** : Created when you generate an API key.
  * A **Consumer Secret** : Created when you generate an API key.
  * A **WooCommerce URL**



To generate an API key and set up your credential:

  1. Go to **WooCommerce > Settings > Advanced > Rest API > Add key**.
  2. Select **Read/Write** from the **Permissions** dropdown.
  3. Copy the generated **Consumer Key** and **Consumer Secret** and enter them into your n8n credentials.
  4. Enter your WordPress site URL as the **WooCommerce URL**.
  5. By default, n8n passes your credential details in the Authorization header. If you need to pass them as query string parameters instead, turn on **Include Credentials in Query**.



Refer to [Generate Keys](https://developer.woocommerce.com/docs/getting-started-with-the-woocommerce-rest-api/#3-generate-keys) for more information.

## Resolve "Consumer key is missing" error#

When you try to connect your credentials, you may receive an error like this: `Consumer key is missing`.

This occurs when the server can't parse the Authorization header details when authenticating over SSL.

To resolve it, turn on the **Include Credentials in Query** toggle to pass the consumer key/secret as query string parameters instead and retry the credential.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

# Adalo credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/adalo.md "Edit this page")

# Adalo credentials#

You can use these credentials to authenticate the following nodes:

  * [Adalo](../../app-nodes/n8n-nodes-base.adalo/)



API access

You need a Team or Business plan to use the Adalo APIs.

## Supported authentication methods#

  * API key



## Related resources#

Refer to [Adalo's API collections documentation](https://help.adalo.com/integrations/the-adalo-api/collections) for more information about working with the service.

## Using API key#

To configure this credential, you'll need an [Adalo](https://www.adalo.com/) account and:

  * An **API Key**
  * An **App ID**



To get these, create an Adalo app:

  1. From the app dropdown in the top navigation, select **CREATE NEW APP**.
  2. Select the App Layout type that makes sense for you and select **Next**.
     * If you're new to using the product, Adalo recommend using **Mobile Only**.
  3. Select a template to get started with or select **Blank** , then select **Next**.
  4. Enter an **App Name** , like `n8n integration`.
  5. If applicable, select the **Team** for the app.
  6. Select branding colors.
  7. Select **Create**. The app editor opens.
  8. In the left menu, select **Settings** (the gear cog icon).
  9. Select **App Access**.
  10. In the **API Key** section, select **Generate Key**.
     * If you don't have the correct plan level, you'll see a prompt to upgrade instead.
  11. Copy the key and enter it as the **API Key** in your n8n credential.
  12. The URL includes the **App ID** after `https://app.adalo.com/apps/`. For example, if the URL for your app is `https://app.adalo.com/apps/b78bdfcf-48dc-4550-a474-dd52c19fc371/app-settings`, `b78bdfcf-48dc-4550-a474-dd52c19fc371` is the App ID. Copy this value and enter it in your n8n credential.



Refer to [Creating an app](https://help.adalo.com/design/designing-your-app/creating-an-app) for more information on creating apps in Adalo. Refer to [The Adalo API](https://help.adalo.com/integrations/the-adalo-api) for more information on generating API keys.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

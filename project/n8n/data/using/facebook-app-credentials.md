# Facebook App credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/facebookapp.md "Edit this page")

# Facebook App credentials#

You can use these credentials to authenticate the following nodes:

  * [Facebook Trigger](../../trigger-nodes/n8n-nodes-base.facebooktrigger/)



Facebook Graph API credentials

If you want to create credentials for the [Facebook Graph API](../../app-nodes/n8n-nodes-base.facebookgraphapi/) node, follow the instructions in the [Facebook Graph API credentials](../facebookgraph/) documentation.

## Supported authentication methods#

  * App access token



## Related resources#

Refer to [Meta's Graph API documentation](https://developers.facebook.com/docs/graph-api/overview) for more information about the service.

## Using app access token#

To configure this credential, you'll need a [Meta for Developers](https://developers.facebook.com/) account and:

  * An app **Access Token**
  * An optional **App Secret** : Used to verify the integrity and origin of the payload.



There are five steps in setting up your credential:

  1. Create a Meta app with the Webhooks product.
  2. Generate an App Access Token for that app.
  3. Configure the Facebook trigger.
  4. Optional: Add an app secret.
  5. App Review: Only required if your app's users don't have roles on the app itself. If you're creating the app for your own internal purposes, this isn't necessary.



Refer to the detailed instructions below for each step.

### Create a Meta app#

To create a Meta app:

  1. Go to the Meta Developer [App Dashboard](https://developers.facebook.com/apps) and select **Create App**.
  2. If you have a business portfolio and you're ready to connect the app to it, select the business portfolio. If you don't have a business portfolio or you're not ready to connect the app to the portfolio, select **I don’t want to connect a business portfolio yet** and select **Next**. The **Use cases** page opens.
  3. Select **Other** , then select **Next**.
  4. Select **Business** and **Next**.
  5. Complete the essential information:
     * Add an **App name**.
     * Add an **App contact email**.
     * Here again you can connect to a business portfolio or skip it.
  6. Select **Create app**.
  7. The **Add products to your app** page opens.
  8. Select **App settings > Basic** from the left menu.
  9. Enter a **Privacy Policy URL**. (Required to take the app "Live.")
  10. Select **Save changes**.
  11. At the top of the page, toggle the **App Mode** from **Development** to **Live**.
  12. In the left menu, select **Add Product**.
  13. The **Add products to your app** page appears. Select **Webhooks**.
  14. The **Webhooks** product opens.



Refer to Meta's [Create an app](https://developers.facebook.com/docs/development/create-an-app) documentation for more information on creating an app, required fields like the Privacy Policy URL, and adding products.

For more information on the app modes and switching to **Live** mode, refer to [App Modes](https://developers.facebook.com/docs/development/build-and-test/app-modes) and [Publish | App Types](https://developers.facebook.com/docs/development/release#app-types).

### Generate an App Access Token#

Next, create an app access token to be used by your n8n credential and the Webhooks product:

  1. In a separate tab or window, open the [Graph API explorer](https://developers.facebook.com/tools/explorer/).
  2. Select the **Meta App** you just created in the **Access Token** section.
  3. In **User or Page** , select **Get App Token**.
  4. Select **Generate Access Token**.
  5. The page prompts you to log in and grant access. Follow the on-screen prompts.

App unavailable

You may receive a warning that the app isn't available. Once you take an app live, there may be a few minutes' delay before you can generate an access token.

  6. Copy the token and enter it in your n8n credential as the **Access Token**. Save this token somewhere else, too, since you'll need it for the Webhooks configuration.

  7. Save your n8n credential.



Refer to the Meta instructions for [Your First Request](https://developers.facebook.com/docs/graph-api/get-started#get-started) for more information on generating the token.

### Configure the Facebook Trigger#

Now that you have a token, you can configure the Facebook Trigger node:

  1. In your Meta app, copy the **App ID** from the top navigation bar.
  2. In n8n, open your Facebook Trigger node.
  3. Paste the **App ID** into the **APP ID** field.
  4. Select **Test step** to shift the trigger into listening mode.
  5. Return to the tab or window where your Meta app's **Webhooks** product configuration is open.
  6. **Subscribe** to the objects you want to receive Facebook Trigger notifications about. For each subscription:
     1. Copy the **Webhook URL** from n8n and enter it as the **Callback URL** in your Meta App.
     2. Enter the **Access Token** you copied above as the **Verify token**.
     3. Select **Verify and save**. (This step fails if you don't have your n8n trigger listening.)
     4. Some webhook subscriptions, like **User** , prompt you to subscribe to individual events. Subscribe to the events you're interested in.
     5. You can send some **Test** events from Meta to confirm things are working. If you send a test event, verify its receipt in n8n.



Refer to the [Facebook Trigger node](../../trigger-nodes/n8n-nodes-base.facebooktrigger/) documentation for more information.

### Optional: Add an App Secret#

For added security, Meta recommends adding an **App Secret**. This signs all API calls with the `appsecret_proof` parameter. The app secret proof is a sha256 hash of your access token, using your app secret as the key.

To generate an App Secret:

  1. In Meta while viewing your app, select **App settings > Basic** from the left menu.
  2. Select **Show** next to the **App secret** field.
  3. The page prompts you to re-enter your Facebook account credentials. Once you do so, Meta shows the App Secret.
  4. Highlight it to select it, copy it, and paste this into your n8n credential as the **App Secret**.
  5. **Save** your n8n credential.



Refer to the [App Secret documentation](https://developers.facebook.com/docs/facebook-login/security#appsecret) for more information.

### App review#

App Review requires Business Verification.

Your app must go through App Review if it will be used by someone who:

  * Doesn't have a role on the app itself.
  * Doesn't have a role in the Business that has claimed the app.



If your only app users are users who have a role on the app itself, App Review isn't required.

As part of the App Review process, you may need to request advanced access for your webhook subscriptions.

Refer to Meta's [App Review](https://developers.facebook.com/docs/resp-plat-initiatives/app-review) and [Advanced Access](https://developers.facebook.com/docs/graph-api/overview/access-levels#advanced-access) documentation for more information.

## Common issues#

### Unverified apps limit#

Facebook only lets you have a developer or administrator role on a maximum of 15 apps that aren't already linked to a Meta Verified Business Account.

Refer to [Limitations | Create an app](https://developers.facebook.com/docs/development/create-an-app#limitations) if you're over that limit.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

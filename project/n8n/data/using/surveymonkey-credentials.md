# SurveyMonkey credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/surveymonkey.md "Edit this page")

# SurveyMonkey credentials#

You can use these credentials to authenticate the following nodes:

  * [SurveyMonkey Trigger](../../trigger-nodes/n8n-nodes-base.surveymonkeytrigger/)



## Prerequisites#

  * Create a [SurveyMonkey](https://www.surveymonkey.com) account.
  * [Register an app](https://api.surveymonkey.com/v3/docs?api_key=3yr7n6m8sjwvm48x8nhxej52#registering-an-app) from your [**Developer dashboard > My apps**](https://developer.surveymonkey.com/apps/).
    * Refer to Required app scopes for information on the scopes you must use.



## Supported authentication methods#

  * API access token
  * OAuth2



## Related resources#

Refer to [SurveyMonkey's API documentation](https://developer.surveymonkey.com/api/v3/#SurveyMonkey-Api) for more information about the service.

## Using API access token#

To configure this credential, you'll need:

  * An **Access Token** : Generated once you create an app.
  * A **Client ID** : Generated once you create an app.
  * A **Client Secret** : Generated once you create an app.



Once you've created your app and assigned appropriate scopes, go to **Settings > Credentials**. Copy the **Access Token** , **Client ID** , and **Secret** and add them to n8n.

## Using OAuth#

To configure this credential, you'll need:

  * A **Client ID** : Generated once you create an app.
  * A **Client Secret** : Generated once you create an app.



Once you've created your app and assigned appropriate scopes:

  1. Go to the app's **Settings > Settings**.
  2. From n8n, copy the **OAuth Redirect URL**.
  3. Overwrite the app's existing **OAuth Redirect URL** with that URL.
  4. Select **Submit Changes**.
  5. Be sure the **Scopes** section contains the Required app scopes.



From the app's **Settings > Credentials**, copy the **Client ID** and **Client Secret** and add them to your n8n credential. You can now select **Connect my account** from n8n.

SurveyMonkey Test OAuth Flow

This option only works if you keep the default SurveyMonkey **OAuth Redirect URL** and add the n8n OAuth Redirect URL as an **Additional Redirect URL**.

## Required app scopes#

Once you create your app, go to **Settings > Scopes**. Select these scopes for your n8n credential to work:

  * **View Surveys**
  * **View Collectors**
  * **View Responses**
  * **View Response Details**
  * **Create/Modify Webhooks**
  * **View Webhooks**



Select **Update Scopes** to save them.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

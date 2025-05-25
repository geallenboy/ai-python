# Google OAuth2 single service

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/google/oauth-single-service.md "Edit this page")

# Google: OAuth2 single service#

This document contains instructions for creating a Google credential for a single service. They're also available as a video.

Note for n8n Cloud users

For the following nodes, you can authenticate by selecting **Sign in with Google** in the OAuth section: 

  * [Google Calendar](../../../app-nodes/n8n-nodes-base.googlecalendar/)
  * [Google Contacts](../../../app-nodes/n8n-nodes-base.googlecontacts/)
  * [Google Drive](../../../app-nodes/n8n-nodes-base.googledrive/)
  * [Google Mail](../../../app-nodes/n8n-nodes-base.gmail/)
  * [Google Sheets](../../../app-nodes/n8n-nodes-base.googlesheets/)
  * [Google Sheets Trigger](../../../trigger-nodes/n8n-nodes-base.googlesheetstrigger/)
  * [Google Tasks](../../../app-nodes/n8n-nodes-base.googletasks/)



## Prerequisites#

  * Create a [Google Cloud](https://cloud.google.com/) account.



## Set up OAuth#

There are five steps to connecting your n8n credential to Google services:

  1. Create a Google Cloud Console project.
  2. Enable APIs.
  3. Configure your OAuth consent screen.
  4. Create your Google OAuth client credentials.
  5. Finish your n8n credential.



### Create a Google Cloud Console project#

First, create a Google Cloud Console project. If you already have a project, jump to the next section:

  1. Log in to your [Google Cloud Console](https://console.cloud.google.com) using your Google credentials.
  2. In the top menu, select the project dropdown in the top navigation and select **New project** or go directly to the [New Project](https://console.cloud.google.com/projectcreate) page.
  3. Enter a **Project name** and select the **Location** for your project.
  4. Select **Create**.
  5. Check the top navigation and make sure the project dropdown has your project selected. If not, select the project you just created.

[![The project dropdown in the Google Cloud top navigation](../../../../../_images/integrations/builtin/credentials/google/google-cloud-project-dropdown.png)](https://docs.n8n.io/_images/integrations/builtin/credentials/google/google-cloud-project-dropdown.png) Check the project dropdown in the Google Cloud top navigation




### Enable APIs#

With your project created, enable the APIs you'll need access to:

  1. Access your [Google Cloud Console - Library](https://console.cloud.google.com/apis/library). Make sure you're in the correct project.  [![The project dropdown in the Google Cloud top navigation](../../../../../_images/integrations/builtin/credentials/google/google-cloud-project-dropdown.png)](https://docs.n8n.io/_images/integrations/builtin/credentials/google/google-cloud-project-dropdown.png) Check the project dropdown in the Google Cloud top navigation
  2. Go to **APIs & Services > Library**.
  3. Search for and select the API(s) you want to enable. For example, for the Gmail node, search for and enable the Gmail API.
  4. Some integrations require other APIs or require you to request access:

     * Google Perspective: [Request API Access](https://developers.perspectiveapi.com/s/docs-get-started).
     * Google Ads: Get a [Developer Token](https://developers.google.com/google-ads/api/docs/first-call/dev-token).

Google Drive API required

The following integrations require the Google Drive API, as well as their own API:

     * Google Docs
     * Google Sheets
     * Google Slides 

Google Vertex AI API

In addition to the Vertex AI API you will also need to enable the [Cloud Resource Manager API](https://console.cloud.google.com/apis/api/cloudresourcemanager.googleapis.com/).

  5. Select **ENABLE**.




### Configure your OAuth consent screen#

If you haven't used OAuth in your Google Cloud project before, you'll need to [configure the OAuth consent screen](https://developers.google.com/workspace/guides/configure-oauth-consent):

  1. Access your [Google Cloud Console - Library](https://console.cloud.google.com/apis/library). Make sure you're in the correct project.  [![The project dropdown in the Google Cloud top navigation](../../../../../_images/integrations/builtin/credentials/google/google-cloud-project-dropdown.png)](https://docs.n8n.io/_images/integrations/builtin/credentials/google/google-cloud-project-dropdown.png) Check the project dropdown in the Google Cloud top navigation
  2. Open the left navigation menu and go to **APIs & Services > OAuth consent screen**.
  3. For **User Type** , select **Internal** for user access within your organization's Google workspace or **External** for any user with a Google account. Refer to Google's [User type documentation](https://support.google.com/cloud/answer/10311615#user-type&zippy=%2Cexternal%2Cinternal) for more information on user types.
  4. Select **Create**.
  5. Enter the essential information:
     * **App name**
     * **User support email**
     * **Email addresses** field in **Developer contact information**
  6. In the **Authorized domains** section, add `n8n.cloud` if using n8n's Cloud service. If you're [self-hosting](../../../../../hosting/), add the domain of your n8n instance.
  7. Select **SAVE AND CONTINUE** to go to the **Scopes** page.
  8. You don't need to set any scopes. Select **SAVE AND CONTINUE** again to go to the **Summary** page.
  9. On the **Summary** page, review the information for accuracy.



### Create your Google OAuth client credentials#

Next, create the OAuth client credentials in Google:

  1. In the **APIs & Services** section, select **Credentials**.
  2. Select **\+ CREATE CREDENTIALS > OAuth client ID**.
  3. In the **Application type** dropdown, select **Web application**.
  4. Google automatically generates a **Name**. Update the **Name** to something you'll recognize in your console.
  5. From your n8n credential, copy the **OAuth Redirect URL**. Paste it into the **Authorized redirect URIs** in Google Console.
  6. Select **CREATE**.



### Finish your n8n credential#

With the Google project and credentials fully configured, finish the n8n credential:

  1. From Google's **OAuth client created** modal, copy the **Client ID**. Enter this in your n8n credential.
  2. From the same Google modal, copy the **Client Secret**. Enter this in your n8n credential.
  3. In n8n, select **Sign in with Google** to complete your Google authentication.
  4. **Save** your new credentials.



## Video#

## Troubleshooting#

### Google hasn't verified this app#

If using the OAuth authentication method, you might see the warning **Google hasn't verified this app**. To avoid this, you can create OAuth credentials from the same account you want to authenticate. 

If you need to use credentials generated by another account (by a developer or another third party), follow the instructions in [Google Cloud documentation | Authorization errors: Google hasn't verified this app](https://developers.google.com/nest/device-access/reference/errors/authorization#google_hasnt_verified_this_app).

### Google Cloud app becoming unauthorized#

For Google Cloud apps with **Publishing status** set to **Testing** and **User type** set to **External** , consent and tokens expire after seven days. Refer to [Google Cloud Platform Console Help | Setting up your OAuth consent screen](https://support.google.com/cloud/answer/10311615?hl=en#zippy=%2Ctesting) for more information. To resolve this, reconnect the app in the n8n credentials modal.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

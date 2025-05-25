# Set up SAML

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/user-management/saml/setup.md "Edit this page")

# Set up SAML#

Feature availability

  * Available on Enterprise plans.
  * You need access to the n8n instance owner account to enable and configure SAML



Available from version 0.225.0.

This page tells you how to enable SAML SSO (single sign-on) in n8n. It assumes you're familiar with SAML. If you're not, [SAML Explained in Plain English](https://www.onelogin.com/learn/saml) can help you understand how SAML works, and its benefits.

## Enable SAML#

  1. In n8n, go to **Settings** > **SSO**.
  2. Make a note of the n8n **Redirect URL** and **Entity ID**.
     1. **Optional** : if your IdP allows you to set up SAML from imported metadata, navigate to the **Entity ID** URL and save the XML. 
     2. **Optional** : if you are running n8n behind a load balancer make sure you have `N8N_EDITOR_BASE_URL` configured. 
  3. Set up SAML with your IdP (identity provider). You need the redirect URL and entity ID. You may also need an email address and name for the IdP user.
  4. After completing setup in your IdP, load the metadata XML into n8n. You can use a metadata URL or raw XML:
     1. **Metadata URL** : Copy the metadata URL from your IdP into the **Identity Provider Settings** field in n8n.
     2. **Raw XML** : Download the metadata XML from your IdP, toggle **Identiy Provider Settings** to **XML** , then copy the raw XML into **Identity Provider Settings**.
  5. Select **Save settings**.
  6. Select **Test settings** to check your SAML setup is working.
  7. Set SAML 2.0 to **Activated**.



## Generic IdP setup#

The steps to configure the IdP vary depending on your chosen IdP. These are some common setup tasks:

  * Create an app for n8n in your IdP.
  * Map n8n attributes to IdP attributes:

Name | Name format | Value (IdP side)  
---|---|---  
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress | URI Reference | User email  
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/firstname | URI Reference | User First Name  
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/lastname | URI Reference | User Last Name  
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn | URI Reference | User Email  
  



## Setup resources for common IdPs#

Documentation links for common IdPs.

IdP | Documentation  
---|---  
Auth0 | [Configure Auth0 as SAML Identity Provider: Manually configure SSO integrations](https://auth0.com/docs/authenticate/protocols/saml/saml-sso-integrations/configure-auth0-saml-identity-provider#manually-configure-sso-integrations)  
Authentik | [Applications](https://goauthentik.io/docs/applications) and the [SAML Provider](https://goauthentik.io/docs/providers/saml/)  
Azure AD | [SAML authentication with Azure Active Directory](https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/auth-saml)  
Keycloak | Choose a [Getting Started](https://www.keycloak.org/guides#getting-started) guide depending on your hosting.  
Okta | n8n provides a [Workforce Identity setup guide](../okta/)  
PingIdentity | [PingOne SSO](https://docs.pingidentity.com/pingone/getting_started_with_pingone/p1_p1sso_start.html)  
  
Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

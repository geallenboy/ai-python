# Hubspot Trigger

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/trigger-nodes/n8n-nodes-base.hubspottrigger.md "Edit this page")

# HubSpot Trigger node#

[HubSpot](https://www.hubspot.com/) provides tools for social media marketing, content management, web analytics, landing pages, customer support, and search engine optimization.

Webhooks

If you activate a second trigger, the previous trigger stops working. This is because the trigger registers a new webhook with HubSpot when activated. HubSpot only allows one webhook at a time. 

Credentials

You can find authentication information for this node [here](../../credentials/hubspot/).

Examples and templates

For usage examples and templates to help you get started, refer to n8n's [HubSpot Trigger integrations](https://n8n.io/integrations/hubspot-trigger/) page.

## Events#

  * Company
    * Created
    * Deleted
    * Property changed
  * Contact
    * Created
    * Deleted
    * Privacy deleted
    * Property changed
  * Conversation
    * Created
    * Deleted
    * New message
    * Privacy deletion
    * Property changed
  * Deal
    * Created
    * Deleted
    * Property changed
  * Ticket
    * Created
    * Deleted
    * Property changed 



## Related resources#

n8n provides an app node for HubSpot. You can find the node docs [here](../../app-nodes/n8n-nodes-base.hubspot/).

View [example workflows and related content](https://n8n.io/integrations/hubspot-trigger/) on n8n's website.

Refer to [HubSpot's documentation](https://developers.hubspot.com/docs/api/overview) for details about their API.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

# Twilio

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.twilio.md "Edit this page")

# Twilio node#

Use the Twilio node to automate work in Twilio, and integrate Twilio with other applications. n8n supports sending MMS/SMS and WhatsApp messages with Twilio. 

On this page, you'll find a list of operations the Twilio node supports and links to more resources.

Credentials

Refer to [Twilio credentials](../../credentials/twilio/) for guidance on setting up authentication. 

This node can be used as an AI tool

This node can be used to enhance the capabilities of an AI agent. When used in this way, many parameters can be set automatically, or with information directed by AI - find out more in the [AI tool parameters documentation](../../../../advanced-ai/examples/using-the-fromai-function/).

## Operations#

  * SMS
    * Send SMS/MMS/WhatsApp message
  * Call
    * Make a phone call using text-to-speech to say a message



## Templates and examples#

**Handling Appointment Leads and Follow-up With Twilio, Cal.com and AI**

by Jimleuk

[View template details](https://n8n.io/workflows/2342-handling-appointment-leads-and-follow-up-with-twilio-calcom-and-ai/)

**Enhance Customer Chat by Buffering Messages with Twilio and Redis**

by Jimleuk

[View template details](https://n8n.io/workflows/2346-enhance-customer-chat-by-buffering-messages-with-twilio-and-redis/)

**Send an SMS/Whatsapp message with Twilio**

by tanaypant

[View template details](https://n8n.io/workflows/401-send-an-smswhatsapp-message-with-twilio/)

[Browse Twilio integration templates](https://n8n.io/integrations/twilio/), or [search all templates](https://n8n.io/workflows/)

## Related resources#

Refer to [Twilio's documentation](https://www.twilio.com/docs/usage/api) for more information about the service.

## What to do if your operation isn't supported#

If this node doesn't support the operation you want to do, you can use the [HTTP Request node](../../core-nodes/n8n-nodes-base.httprequest/) to call the service's API.

You can use the credential you created for this service in the HTTP Request node: 

  1. In the HTTP Request node, select **Authentication** > **Predefined Credential Type**.
  2. Select the service you want to connect to.
  3. Select your credential.



Refer to [Custom API operations](../../../custom-operations/) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

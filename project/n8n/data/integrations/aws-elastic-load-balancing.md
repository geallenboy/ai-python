# AWS Elastic Load Balancing

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.awselb.md "Edit this page")

# AWS Elastic Load Balancing node#

Use the AWS Elastic Load Balancing node to automate work in AWS ELB, and integrate AWS ELB with other applications. n8n has built-in support for a wide range of AWS ELB features, including adding, getting, removing, deleting certificates and load balancers.

On this page, you'll find a list of operations the AWS ELB node supports and links to more resources.

Credentials

Refer to [AWS ELB credentials](../../credentials/aws/) for guidance on setting up authentication. 

## Operations#

  * Listener Certificate
    * Add
    * Get Many
    * Remove
  * Load Balancer
    * Create
    * Delete
    * Get
    * Get Many



This node supports creating and managing application and network load balancers. It doesn't currently support gateway load balancers.

## Templates and examples#

**Transcribe audio files from Cloud Storage**

by Lorena

[View template details](https://n8n.io/workflows/1394-transcribe-audio-files-from-cloud-storage/)

**Extract and store text from chat images using AWS S3**

by Lorena

[View template details](https://n8n.io/workflows/1393-extract-and-store-text-from-chat-images-using-aws-s3/)

**Sync data between Google Drive and AWS S3**

by Lorena

[View template details](https://n8n.io/workflows/1396-sync-data-between-google-drive-and-aws-s3/)

[Browse AWS Elastic Load Balancing integration templates](https://n8n.io/integrations/aws-elb/), or [search all templates](https://n8n.io/workflows/)

## Related resources#

Refer to [AWS ELB's documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html) for more information on this service.

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

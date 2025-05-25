# Blocking nodes

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/hosting/securing/blocking-nodes.md "Edit this page")

# Block access to nodes#

For security reasons, you may want to block your users from accessing or working with specific n8n nodes. This is helpful if your users might be untrustworthy.

Use the `NODES_EXCLUDE` environment variable to prevent your users from accessing specific nodes.

## Exclude nodes#

Update your `NODES_EXCLUDE` environment variable to include an array of strings containing any nodes you want to block your users from using.

For example, setting the variable this way:
    
    
    1

| 
    
    
    NODES_EXCLUDE: "[\"n8n-nodes-base.executeCommand\", \"n8n-nodes-base.readWriteFile\"]"
      
  
---|---  
  
Blocks the [Execute Command](../../../integrations/builtin/core-nodes/n8n-nodes-base.executecommand/) and [Read/Write Files from Disk](../../../integrations/builtin/core-nodes/n8n-nodes-base.readwritefile/) nodes.

Your n8n users won't be able to search for or use these nodes.

## Suggested nodes to block#

The nodes that can pose security risks vary based on your use case and user profile. Here are some nodes you might want to start with:

  * [Execute Command](../../../integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)
  * [Read/Write Files from Disk](../../../integrations/builtin/core-nodes/n8n-nodes-base.readwritefile/)



## Related resources#

Refer to [Nodes environment variables](../../configuration/environment-variables/nodes/) for more information on this environment variable.

Refer to [Configuration](../../configuration/configuration-methods/) for more information on setting environment variables.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

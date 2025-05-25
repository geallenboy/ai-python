# External secrets

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/hosting/configuration/environment-variables/external-secrets.md "Edit this page")

# External secrets environment variables#

File-based configuration

You can add `_FILE` to individual variables to provide their configuration in a separate file. Refer to [Keeping sensitive data in separate files](../../configuration-methods/#keeping-sensitive-data-in-separate-files) for more details.

You can use an external secrets store to manage credentials for n8n. Refer to [External secrets](../../../../external-secrets/) for details.

Variable | Type | Default | Description  
---|---|---|---  
`N8N_EXTERNAL_SECRETS_UPDATE_INTERVAL` | Number | `300` (5 minutes) | How often (in seconds) to check for secret updates.  
  
Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

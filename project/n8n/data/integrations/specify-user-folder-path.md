# Specify user folder path

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/hosting/configuration/configuration-examples/user-folder.md "Edit this page")

# Specify user folder path#

n8n saves user-specific data like the encryption key, SQLite database file, and the ID of the tunnel (if used) in the subfolder `.n8n` of the user who started n8n. It's possible to overwrite the user-folder using an environment variable.
    
    
    1

| 
    
    
    export N8N_USER_FOLDER=/home/jim/n8n
      
  
---|---  
  
Refer to [Environment variables reference](../../environment-variables/deployment/) for more information on this variable.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

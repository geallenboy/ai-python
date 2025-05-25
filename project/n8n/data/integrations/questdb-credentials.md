# QuestDB credentials

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/credentials/questdb.md "Edit this page")

# QuestDB credentials#

You can use these credentials to authenticate the following nodes:

  * [QuestDB](../../app-nodes/n8n-nodes-base.questdb/)



## Prerequisites#

Create a user account on an instance of [QuestDB](https://questdb.io/).

## Supported authentication methods#

  * Database connection



## Related resources#

Refer to [QuestDB's documentation](https://questdb.io/docs) for more information about the service.

## Using database connection#

To configure this credential, you'll need:

  * The **Host** : Enter the host name or IP address for the server.
  * The **Database** : Enter the database name, for example `qdb`.
  * A **User** : Enter the username for the user account as configured in `pg.user` or `pg.readonly.user` property in `server.conf`. Default value is `admin`.
  * A **Password** : Enter the password for the user account as configured in `pg.password` or `pg.readonly.password` property in `server.conf`. Default value is `quest`.
  * **SSL** : Select whether the connection should use SSL, which sets the `sslmode` parameter. Options include:
    * **Allow**
    * **Disable**
    * **Require**
  * The **Port** : Enter the port number to use for the connection. Default is `8812`.



Refer to [List of supported connection properties](https://questdb.io/docs/reference/api/postgres/#list-of-supported-connection-properties) for more information.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

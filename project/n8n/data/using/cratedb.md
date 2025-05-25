# CrateDB

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.cratedb.md "Edit this page")

# CrateDB node#

Use the CrateDB node to automate work in CrateDB, and integrate CrateDB with other applications. n8n has built-in support for a wide range of CrateDB features, including executing, inserting, and updating rows in the database.

On this page, you'll find a list of operations the CrateDB node supports and links to more resources.

Credentials

Refer to [CrateDB credentials](../../credentials/cratedb/) for guidance on setting up authentication. 

## Operations#

  * Execute an SQL query
  * Insert rows in database
  * Update rows in database



## Templates and examples#

[Browse CrateDB integration templates](https://n8n.io/integrations/cratedb/), or [search all templates](https://n8n.io/workflows/)

## Node reference#

### Specify a column's data type#

To specify a column's data type, append the column name with `:type`, where `type` is the data type you want for the column. For example, if you want to specify the type `int` for the column **id** and type `text` for the column **name** , you can use the following snippet in the **Columns** field: `id:int,name:text`.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

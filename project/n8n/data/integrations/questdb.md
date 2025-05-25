# QuestDB

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.questdb.md "Edit this page")

# QuestDB node#

Use the QuestDB node to automate work in QuestDB, and integrate QuestDB with other applications. n8n supports executing an SQL query and inserting rows in a database with QuestDB.

On this page, you'll find a list of operations the QuestDB node supports and links to more resources.

Credentials

Refer to [QuestDB credentials](../../credentials/questdb/) for guidance on setting up authentication. 

## Operations#

  * Executes a SQL query.
  * Insert rows in database.



## Templates and examples#

[Browse QuestDB integration templates](https://n8n.io/integrations/questdb/), or [search all templates](https://n8n.io/workflows/)

## Node reference#

### Specify a column's data type#

To specify a column's data type, append the column name with `:type`, where `type` is the data type you want for column. For example, if you want to specify the type `int` for the column **id** and type `text` for the column **name** , you can use the following snippet in the **Columns** field: `id:int,name:text`.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

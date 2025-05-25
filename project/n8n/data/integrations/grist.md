# Grist

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/app-nodes/n8n-nodes-base.grist.md "Edit this page")

# Grist node#

Use the Grist node to automate work in Grist, and integrate Grist with other applications. n8n has built-in support for a wide range of Grist features, including creating, updating, deleting, and reading rows in a table. 

On this page, you'll find a list of operations the Grist node supports and links to more resources.

Credentials

Refer to [Grist credentials](../../credentials/grist/) for guidance on setting up authentication. 

## Operations#

  * Create rows in a table
  * Delete rows from a table
  * Read rows from a table
  * Update rows in a table



## Templates and examples#

[Browse Grist integration templates](https://n8n.io/integrations/grist/), or [search all templates](https://n8n.io/workflows/)

## Get the Row ID#

To update or delete a particular record, you need the Row ID. There are two ways to get the Row ID:

**Create a Row ID column in Grist**

Create a new column in your Grist table with the formula `$id`.

**Use the Get All operation**

The **Get All** operation returns the Row ID of each record along with the fields.

You can get it with the expression `{{$node["GristNodeName"].json["id"]}}`.

## Filter records when using the Get All operation#

  * Select **Add Option** and select **Filter** from the dropdown list.
  * You can add filters for any number of columns. The result will only include records which match all the columns.
  * For each column, you can enter any number of values separated by commas. The result will include records which match any of the values for that column.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

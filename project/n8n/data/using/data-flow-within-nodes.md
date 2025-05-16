# Data flow within nodes

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/data/data-flow-nodes.md "Edit this page")

# Data flow within nodes#

Nodes can process multiple items.

For example, if you set the Trello node to `Create-Card`, and create an expression that sets `Name` using a property called `name-input-value` from the incoming data, the node creates a card for each item, always choosing the `name-input-value` of the current item.

For example, this input will create two cards. One named `test1` the other one named `test2`:
    
    
    1
    2
    3
    4
    5
    6
    7
    8

| 
    
    
    [
    	{
    		name-input-value: "test1"
    	},
    	{
    		name-input-value: "test2"
    	}
    ]
      
  
---|---  
  
Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

# Set up your development environment

[ ](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/creating-nodes/build/node-development-environment.md "Edit this page")

# Set up your development environment#

This document lists the essential dependencies for developing a node, as well as guidance on setting up your editor.

## Requirements#

To build and test a node, you need: 

  * Node.js and npm. Minimum version Node 18.17.0. You can find instructions on how to install both using nvm (Node Version Manager) for Linux, Mac, and WSL (Windows Subsystem for Linux) [here](https://github.com/nvm-sh/nvm). For Windows users, refer to Microsoft's guide to [Install NodeJS on Windows](https://docs.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-windows).
  * A local instance of n8n. You can install n8n with `npm install n8n -g`, then follow the steps in [Run your node locally](../../test/run-node-locally/) to test your node.



You should also have [git](https://git-scm.com/) installed. This allows you to clone and use the [n8n-node-starter](https://github.com/n8n-io/n8n-nodes-starter).

## Editor setup#

n8n recommends using [VS Code](https://code.visualstudio.com/) as your editor.

Install these extensions:

  * [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
  * [EditorConfig](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
  * [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)



By using VS Code and these extensions, you get access to the n8n node linter's warnings as you code.

Was this page helpful? 

Thanks for your feedback! 

Thanks for your feedback! Help us improve this page by submitting an issue or a fix in our [GitHub repo](https://github.com/n8n-io/n8n-docs). 

Back to top 

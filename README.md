Fauxpilot commercial setup documentation

Note:  These instructions will only work for azure commercial clouds, i.e. portal.azure.com  
    Fauxpilot for Azure Government can be found in either:
        - https://github.com/robdisney/fauxpilotgov
        - https://hub.docker.com/robdisney/fauxpilotgov 
    These instructions assume you already have an azure tenant, subscription, Log Analytics Workspace with Sentinel deployed, and permissions to perform the actions below.

Open the Azure Commercial Portal
- https://portal.azure.com
- Sign in with your credentials

Key Vault Initial Setup
- Create new key vault for your faux pilot project
- Assign yourself key vault secrets officer
    - Select “Access Control” blade at left
    - Select “Add Role Assignment” at bottom
    - Select “Key Vault Secrets Officer” from the list
    - Click “Next” at bottom
    - Ensure “User, group, or service principal” is selected
    - Click “Add Members”
    - Find and select your user (or users) 
    - Ensure your users are listed under “Selected Members” at bottom
    - Click “Select” at bottom
    - Click “Review and Assign” at the bottom of the page
    - Click “Review and Assign” again

Key Vault Keys
- Open your key vault
- Select “Secrets” blade from the left of the screen
- Create 8 new secrets with the following names:
    - aoai-api-version
    - aoai-deployment
    - aoai-endpoint
    - aoai-key
    - sentinel-api-version
    - sentinel-resource-group
    - sentinel-subscription-id
    - sentinel-workspace-name
- Assign each of them their respective values

Create your Fauxpilot Web App
- From the azure portal home page, type “app services” in the search bar
- Select “App Services” from the drop down list
- At the App Services window, click “Create”
- Choose your desired subscription and resource group
- Choose a unique name (i.e. fauxpilot-webapp-#####)
- Choose “Docker Container”
- For operating system, choose “Linux”
- Choose Region (if it fails to deploy, try a different region)
- Choose your pricing plan
- Click “Next: Database” 
    - Make no changes on this page
- Click “Next: Docker”
    - Click the drop down that says “Quickstart” and Choose “Docker Hub” instead
    - Under “Image and Tag” type:  robdisney/fauxpilotgov:latest
- Click “Next: Networking”
    - Make no changes on this page
- Click “Next: Monitoring”
    - Make changes if desired
- Click “Next: Tags”
    - Add tags if desired
- Click “Next: Review and Create”
- Click “Review and Create”
- Once your app service is created, click “Go to Resource” 

Modify web app
- Stop the web app via “Stop” at the top
- From the left navigation, click “Environment Variables”
- Under “Environment Variables”, click “Add”
    - Under Name, type: KEY_VAULT_URI
    - Under Value, enter your key vault address, 
    - Click apply
- Click Apply again and select Confirm to save the variable

Give the web app a System-assigned Identity
- Click on “Identity” blade
- In center of screen, change status slider to “On”
- Click “Save”
    - At the pop up that reads “Enable System Assigned Managed Identity”, click Yes

Set up authentication to the website
- On the left, choose “Authentication”
- Choose “Add identity provider”
    - Under “Select Identity Provider”, choose “Microsoft”
    - Ensure “Create New App Registration” is selected
    - Under Client Secret Expiration, choose your expiration period (180 days is default)
    - Under “supported account types”, choose whom you want to be able to use your app (I recommend Current Tenant)
    - Leave the remainder of the items at default
 - Save
    
Add key vault permissions for app
- On your faux pilot key vault, select “Access Control”
- Select “Add Role Assignment”
- Select “Key Vault Secrets User” and click “Next”
- On the next screen, select “Managed Identity”, then click the “+ select members” symbol below it
- From the pop-out on the right, select the managed identity drop-down and click “App Service”
- Click on your Fauxpilot app service name
- Click “Select” at the bottom of the pop-out
- Click “Review and Assign” at the bottom of the page
- Click “Review and Assign” again
- Now your fauxpilot app can read all the secrets in the fauxpilot key vault

Add Log Analytics permissions for app
- Open your selected Log Analytics Workspace
- Click on Access Control
- Select “Add Role Assignment”
- Select “Microsoft Sentinel Responder” and click “Next”
- On the next screen, select “Managed Identity”, then click the “+ select members” symbol below it
- From the pop-out on the right, select the managed identity drop-down and click “App Service”
- Click on your Fauxpilot app service name
- Click “Select” at the bottom of the pop-out
- Click “Review and Assign” at the bottom of the page
- Click “Review and Assign” again
- Now your fauxpilot app can use the Log Analytics Workspace for the Sentinel instance

Start your Fauxpilot web app
- Return to the Fauxpilot web app service
- Select Overview blade if not already there
- Click “Start” at the top

Open your new Fauxpilot web app
- On the Fauxpilot web app service Overview page, hover over “default domain” at top right and click the “copy to clipboard” icon that pops up to the right of it
- In your browser, open a new tab
- Use control-v or right click and paste in the address bar and click “return”
- If it does not work immediately, give it a few minutes for the url to propagate through dns and try again.

Make your first query
- In the “Incident Number” text entry at bottom, enter your incident number
- In the “Your Message” text entry at bottom, enter your question about the incident
- Press enter from within the Your Message field
- Wait for the answer

A few notes: 
- The interface is not fast.  It is not currently built for asynchronous response, so you do not see the response until the entire question has been built on the Azure OpenAI side.  Be patient.  

# fauxpilot
Generative AI enablement for Microsoft Security

These scripts broker a transaction between Microsoft Sentinel API and Azure OpenAI services.  This allows an Azure OpenAI model (i.e. gpt3, gpt4) to analyze a microsoft incident at the user's request.

Fauxpilot: "fauxpilot.py" grants the user the ability to enter an incident number (i.e. 101, 1248, etc) and then ask questions about the specified incident.  The user can request to restart and ask a new question about a new incident.  SentinelGPT.py allows a user to enter an incident number, and chatgpt will analyze that incident number and directly inject a detailed incident report to Sentinel's "activity log", and individual remediation checklist items into Sentinel's "Tasks" function.  The user can then access these reports/tasks through the Sentinel Incident panel.

As currently written, both of these scripts are designed to be run from an Azure Machine Learning notebook.  They can be launched from within Sentinel or from the azure machine learning function.

Environment Requirements:
- An Azure Key Vault with the following secrets:
    - version (eg: 03-31-2023) # The most current sentinel API version.  Check Sentinel Rest API documentation at learn.microsoft.com/
    - base (eg: https://gpt-4.openai.azure.com/ # The name of your Azure OpenAI instance
    - key (eg: 209387102938s2af908wj3lkwejr89pp3j2) # Your Azure OpenAI API key
    - model (eg: gpt4) # whatever you named your specific Azure OpenAI model deployment
    - subscription-id (eg: a05016a1-fbe5-4d43-b569-ebddccaf5069) # Your subscription ID where Sentinel lives
    - resource-group (eg: myResourceGroup) # Resource Group where Sentinel lives
    - workspace-name (eg: myLogAnalyticsWorkspace) # Log Analytics Workspace where Sentinel Lives
 
  - An Azure Machine Learning Workspace with CPU compute
  - An Azure OpenAI Instance with a deployed Azure OpenAI Model
  - A Log Analytics Workspace
  - A Sentinel instance deployed to the Log Analytics Workspace
  - All privileges associated with administering the above services
    - In Azure Key Vault, assign role "Key Vault Secrets User" to the Azure Machine Learning instance's managed identity
    - In Log Analytics Workspace, assign role "Sentinel Responder" to the Azure Machine Learning instance's managed identity
   
Future iterations of this effort will include Azure Functions that will automate the injectReport and injectTasks functions as part of a Logic App.  Then, every time a new Sentinel Incident is created, the app can automatically inject tasks and an incident report into the sentinel incident page, saving triage analysts time and energy.

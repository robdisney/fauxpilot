# fauxpilot
Generative AI enablement for Microsoft Security

DISCLAIMER: 
This solution was developed entirely by its author as a personal project.  The code is intended to extend a capability of Generative AI to Microsoft Sentinel.  It should not be viewed as a drop-in replacement for Microsoft Copilot for Security.  In its current form, Fauxpilot much less capable than the expansive offerings of CfS, but does provide the ability to query an LLM about Sentinel Incidents. The Fauxpilot capability and associated scripts herein are not officially supported by Microsoft, though all of its core components are fully supported (Azure Key Vault, Azure Machine Learning Workspace, Azure OpenAI instance, Azure Log Analytics, Microsoft Sentinel, Jupyter Notebooks, etc).  User accepts all risk associated with its use.  User should employ extensive testing and evaluation before deploying to a production environment, and even then should verify the information contained within Fauxpilot response. Author bears no responsibility for loss or damages resulting from its use.  User may modify at will to suit their needs. Happy coding!

OVERVIEW:
These scripts broker a transaction between Microsoft Sentinel API and Azure OpenAI services.  This allows an Azure OpenAI model (i.e. gpt3, gpt4) to analyze a microsoft incident at the user's request.

PURPOSE:
Fauxpilot: "fauxpilot.py" grants the user the ability to enter an incident number (i.e. 101, 1248, etc) and then ask questions about the specified incident.  The user can request to restart and ask a new question about a new incident.  SentinelGPT.py allows a user to enter an incident number, and chatgpt will analyze that incident number and directly inject a detailed incident report to Sentinel's "activity log", and individual remediation checklist items into Sentinel's "Tasks" function.  The user can then access these reports/tasks through the Sentinel Incident panel.

As currently written, both of these scripts are designed to be run from an Azure Machine Learning notebook.  They can be launched from within Sentinel or from the azure machine learning function.

ENVIRONMENT REQUIREMENTS:
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
  - 
PRIVILEGE REQUIREMENTS:
  - Admin must have all privileges associated with creating & administering the above services
    - In Azure Key Vault, assign role "Key Vault Secrets User" to the Azure Machine Learning instance's managed identity
    - In Log Analytics Workspace, assign role "Sentinel Responder" to the Azure Machine Learning instance's managed identity
   
INITIAL SETUP (ONCE REQUIREMENTS ABOVE ARE MET):
- Create a new AML Jupyter notebook called "fauxpilot".
- Create two new files called "fauxpilot.py" and "sentinelgpt.py" and copy/paste the contents of the respective files into your workspace
- Update the keyvault endpoint with your own keyvault name

INITIAL USE (FAUXPILOT):
- Open your FauxPilot Notebook via either Sentinel or the Azure Machine Learning Workspace
- Open a new terminal in the Notebook
- Type "python fauxpilot.py" and press enter.
- When asked what incident you would like to analyze, enter your incident number
- When asked what you want to ask about the incident, enter your question/prompt.

INITIAL USE (SENTINELGPT):
- Open your FauxPilot Notebook via either Sentinel or the Azure Machine Learning Workspace
- Open a new terminal in the Notebook
- Type "python sentinelgpt.py" and press enter.
- When asked what incident you would like to analyze, enter your incident number
- once it runs, go back and check your sentinel incident.  Note: You may need to refresh/reload the page to view the newly-commented incident.

SAMPLE PROMPTS:
- "What Mitre attack tactics were employed in the attack, and what can they tell me about the attacker?"
- "Write a detailed narrative in paragraph form describing what happened in this incident"
- "How should i respond to this incident?  Should I dismiss, remediate, or escalate to tier 2?"
- "write a detailed remediation checklist to respond to this incident"

LIMITATIONS:
1. The application cannot currently perform cross-incident query or multi-incident aggregation.  
2. Fauxpilot creates very attractive KQL queries to investigate incidents, but rarely work as written.  Some tinkering with RAG architecture (i.e. loading KQL queries into a storage container as RAG data store) may prove effective at improving KQL effectiveness.  A skilled KQL author can easily modify the produced KQL queries to function properly, as they are "mostly" correct.
3. The script does not remember previous queries or responses.  Each query/prompt must be designed its own.  Future iterations may include this capability as token limitations allow.

THE FUTURE:   
Future iterations of this effort will include Azure Functions that will automate the injectReport and injectTasks functions as part of a Logic App.  Then, every time a new Sentinel Incident is created, the app can automatically inject tasks and an incident report into the sentinel incident page, saving triage analysts time and energy.

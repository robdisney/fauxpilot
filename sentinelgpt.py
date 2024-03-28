from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import requests
from openai import AzureOpenAI
import uuid
import json

# Initialize the Azure credential using Managed Identity
credential = DefaultAzureCredential()

# Replace with your Key Vault name (DNS Name)
key_vault_uri = "https://<your_keyvault_name>.vault.azure.net/"

# Initialize the SecretClient
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Retrieve secrets from Azure Key Vault
openaiapi_version = secret_client.get_secret("version").value
openaiapi_base = secret_client.get_secret("base").value
openaiapi_key = secret_client.get_secret("key").value
model = secret_client.get_secret("model").value
subscription_id = secret_client.get_secret("subscription-id").value
resource_group = secret_client.get_secret("resource-group").value
workspace_name = secret_client.get_secret("workspace-name").value

# Initialize the OpenAIAPI client
client = AzureOpenAI(api_version=openaiapi_version,
                     azure_endpoint=openaiapi_base,
                     api_key=openaiapi_key)

# Define class for accessing Sentinel API
class SentinelAPI:
    def __init__(self, subscription_id, resource_group, workspace_name):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.workspace_name = workspace_name
        self.access_token = self.authenticate()

    def authenticate(self):
        # Managed Identity does not require explicit authentication here
        # The token will be automatically managed by DefaultAzureCredential
        return None

    def get_headers(self):
        # Use the token from the DefaultAzureCredential
        token = credential.get_token('https://management.azure.com/.default').token
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
    def get_incidents(self):
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents?api-version=2023-11-01"
        response = requests.get(url, headers=self.get_headers())
        return response.json()
        
    def get_incident_details(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}?api-version=2023-11-01"
        response = requests.get(url, headers=self.get_headers())
        return response.json()
    
    def get_incident_alerts(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/alerts?api-version=2023-11-01"
        response = requests.post(url, headers=self.get_headers())
        return response.json()
    
    def get_incident_entities(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/entities?api-version=2023-11-01"
        response = requests.post(url, headers=self.get_headers())
        return response.json()
    
    def get_incident_relations(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/relations?api-version=2023-11-01"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def inject_report(self, incident_report, incident_id):
        comment_id = uuid.uuid4()
        url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/comments/{comment_id}?api-version=2023-11-01"
        data = {
            "properties": {
            "message": incident_report
            }
        }
        print(data)
        comment_response = requests.put(url, headers=self.get_headers(), data=json.dumps(data))
        print(comment_response.json())
        print("Injecting report into Sentinel Incident")

    def inject_tasks(self, tasks, incident_id):
        for task in tasks['value']:
            task_id = uuid.uuid4()
            url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/tasks/{task_id}?api-version=2023-07-01-preview"
            data = {
                "properties": {
                    "title": task['properties']['title'],
                    "description": task['properties']['description'],
                    "status": "New",
                }
            }
            print(data)
            comment_response = requests.put(url, headers=self.get_headers(), data=json.dumps(data))
            print(comment_response.json())
            print("Injecting task into Sentinel Incident")
        
class ChatGPT:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def generate_response(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.5
        )
        return response.choices[0].message.content

def find_incident_id(incidents, incident_number):
    for incident in incidents.get('value', []):
        if str(incident.get('properties', {}).get('incidentNumber')) == incident_number:
            return incident.get('name')
    return None

# extracts the json file from chatgpt's task creation response
def parse_json(input_string):
    # Find the first opening brace
    start_index = input_string.find('{')
    # Find the last closing brace
    end_index = input_string.rfind('}')
    
    # Check if both braces are found
    if start_index == -1 or end_index == -1:
        raise ValueError("Input string does not contain a valid JSON object.")
    
    # Extract the JSON content
    json_content = input_string[start_index:end_index + 1]
    return json_content

# Main function (this is where the magic happens)
def main():
    sentinel_api = SentinelAPI(subscription_id, resource_group, workspace_name)
    chatgpt = ChatGPT(client, model)

    # Pull all incidents from Sentinel API
    incidents = sentinel_api.get_incidents()
    incident_number = input("Enter the incident number you want to analyze (e.g. 107) or 'quit' to exit: ")
    incident_id = find_incident_id(incidents, incident_number)

    # Pull incident details, alerts, entities, and relations
    incident_details = sentinel_api.get_incident_details(incident_id)
    incident_alerts = sentinel_api.get_incident_alerts(incident_id)
    incident_entities = sentinel_api.get_incident_entities(incident_id)
    incident_relations = sentinel_api.get_incident_relations(incident_id)

    # Send the contents of the user prompt along with alerts, relations, details, and entities to ChatGPT for analysis
    report_context = "You are a cybersecurity expert using Microsoft Sentinel.  Consider the following incident and write an executive summary including the following sections:  1) write a brief paragraph explaining what happened, what it implies, and why it is important to the reader, 2) Create an incident report and timeline about what transpired, 3) Create a detailed remediation checklist to resolve the incident,  4) make a recommendation for either dismissal, remediation, or escalation to tier 2 analysts."

    combined_info = f"{incident_details} {incident_alerts} {incident_entities} {incident_relations}"
    print('Sending data for analysis')
    incident_report = chatgpt.generate_response(report_context + combined_info)
    print('Analysis complete')
    # send the report to sentinel
    print('Injecting report')
    sentinel_api.inject_report(incident_report, incident_id)
    print('Report injected')

    # Begin tasks section
    # Define a JSON format for the response
    taskFormat = '{"value": [{"kind": "remediationTask","properties": {"title": "","description": ""}},{"kind": "remediationTask","properties": {"title": "","description": ""}},{"kind": "remediationTask","properties": {"title": "","description": ""}}]}'

    # Send the contents of the user prompt along with alerts, relations, details, and entities to ChatGPT for analysis
    task_context = "You are a cybersecurity expert using Microsoft Sentinel. Review the incident below and create a checklist of remediation actions you would take to respond to and resolve the incident.  Return your response in json according to this format \n" + taskFormat + ".\n For each task description, reference any machines or entities that must be addressed for that task.  Feel free to add as many additional tasks to the json format as necessary to most effectively resolve the incident"
    # Make the ChatGPT Request
    print('Sending data for analysis')
    incident_tasks = chatgpt.generate_response(task_context + combined_info)
    print('Analysis Complete')
    # Parse out the json file
    json_tasks = parse_json(incident_tasks)
    # Convert to json format
    tasks = json.loads(json_tasks)
    print('Injecting tasks into ')
    sentinel_api.inject_tasks(tasks, incident_id)

if __name__ == "__main__":
    main()

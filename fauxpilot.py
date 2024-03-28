from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import requests
from openai import AzureOpenAI

# Initialize the Azure credential using Managed Identity
credential = DefaultAzureCredential()

# Replace with your Key Vault name (DNS Name)
key_vault_uri = "https://<your_key_vault_name>.vault.azure.net/"

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

class ChatGPT:
    def __init__(self, client, model):
        self.client = client
        self.model = model
      
    # Adjust parameters below to meet your own requirements
    def generate_response(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.5
        )
        return response.choices[0].message.content

def main():
    sentinel_api = SentinelAPI(subscription_id, resource_group, workspace_name)
    chatgpt = ChatGPT(client, model)

    # Pull all incidents from Sentinel API
    incidents = sentinel_api.get_incidents()

    # User interaction loop
    while True:
        # Take user input for incident number
        incident_number = input("Enter the incident number (e.g. 107) or 'quit' to exit: ")
        if incident_number.lower() == 'quit':
            break

        # Find the incident ID based on the incident number
        incident_id = find_incident_id(incidents, incident_number)
        if incident_id:
            # Pull incident details, alerts, entities, and relations
            incident_details = sentinel_api.get_incident_details(incident_id)
            incident_alerts = sentinel_api.get_incident_alerts(incident_id)
            incident_entities = sentinel_api.get_incident_entities(incident_id)
            incident_relations = sentinel_api.get_incident_relations(incident_id)

            while True:
                user_prompt = input(f"What would you like to know about incident number {incident_number}? \n(Type 'restart' to enter a new incident number or 'quit' to exit): ")
                if user_prompt.lower() == 'quit':
                    return
                elif user_prompt.lower() == 'restart':
                    break

                # Send the contents of the user prompt along with alerts, relations, details, and entities to ChatGPT for analysis
                context = "You are a cybersecurity expert using Microsoft Sentinel.  Consider the user request below and respond to their request regarding the specified incident.\n" 
                combined_info = f"{incident_details} {incident_alerts} {incident_entities} {incident_relations}"
                chatgpt_response = chatgpt.generate_response(context + user_prompt + " " + combined_info)
                print(chatgpt_response)
        else:
            print(f"Incident number {incident_number} not found.")

def find_incident_id(incidents, incident_number):
    for incident in incidents.get('value', []):
        if str(incident.get('properties', {}).get('incidentNumber')) == incident_number:
            return incident.get('name')
    return None

if __name__ == "__main__":
    main()

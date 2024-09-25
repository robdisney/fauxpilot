from flask import Flask, render_template, request, jsonify, session
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import requests
from openai import AzureOpenAI
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Initialize the Azure credential using Managed Identity
credential = DefaultAzureCredential()

# Replace with your Key Vault name (DNS Name)
key_vault_uri = os.getenv("KEY_VAULT_URI")

# Initialize the SecretClient
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Retrieve secrets from Azure Key Vault
openaiapi_version = secret_client.get_secret("aoai-api-version").value
openaiapi_base = secret_client.get_secret("aoai-endpoint").value
openaiapi_key = secret_client.get_secret("aoai-key").value
model = secret_client.get_secret("aoai-deployment").value
subscription_id = secret_client.get_secret("sentinel-subscription-id").value
resource_group = secret_client.get_secret("sentinel-resource-group").value
workspace_name = secret_client.get_secret("sentinel-workspace-name").value
sentinelapiversion = secret_client.get_secret("sentinel-api-version").value

# Initialize the OpenAIAPI client
client = AzureOpenAI(api_version=openaiapi_version,
                     azure_endpoint=openaiapi_base,
                     api_key=openaiapi_key)

class SentinelAPI:
    def __init__(self, subscription_id, resource_group, workspace_name):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.workspace_name = workspace_name

    def get_headers(self):
        token = credential.get_token('https://management.azure.com/.default').token
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

    def get_incidents(self):
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents?api-version={sentinelapiversion}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def get_incident_details(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}?api-version={sentinelapiversion}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def get_incident_alerts(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/alerts?api-version={sentinelapiversion}"
        response = requests.post(url, headers=self.get_headers())
        return response.json()

    def get_incident_entities(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/entities?api-version={sentinelapiversion}"
        response = requests.post(url, headers=self.get_headers())
        return response.json()

    def get_incident_relations(self, incident_id):
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}/providers/Microsoft.SecurityInsights/incidents/{incident_id}/relations?api-version={sentinelapiversion}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    incident_number = data.get("incident_number")
    user_input = data.get("user_input")

    sentinel_api = SentinelAPI(subscription_id, resource_group, workspace_name)
    chatgpt = ChatGPT(client, model)

    incidents = sentinel_api.get_incidents()
    incident_id = find_incident_id(incidents, incident_number)
    if incident_id:
        incident_details = sentinel_api.get_incident_details(incident_id)
        incident_alerts = sentinel_api.get_incident_alerts(incident_id)
        incident_entities = sentinel_api.get_incident_entities(incident_id)
        incident_relations = sentinel_api.get_incident_relations(incident_id)

        context = session.get('context', "You are a cybersecurity expert using Microsoft Sentinel. Consider the user request below and respond to their request regarding the specified incident.\n")
        combined_info = f"{incident_details} {incident_alerts} {incident_entities} {incident_relations}"

        chatgpt_response = chatgpt.generate_response(context + user_input + " " + combined_info)

        # Update the session context with the new conversation
        session['context'] = context + "User: " + user_input + "\nFauxpilot: " + chatgpt_response + "\n"

        return jsonify({"response": chatgpt_response})
    else:
        return jsonify({"response": f"Incident number {incident_number} not found."})

@app.route('/new_topic', methods=['POST'])
def new_topic():
    # Clear the conversation context
    session.pop('context', None)
    return jsonify({"response": "New topic started. Please enter a new incident number and your query."})

def find_incident_id(incidents, incident_number):
    for incident in incidents.get('value', []):
        if str(incident.get('properties', {}).get('incidentNumber')) == incident_number:
            return incident.get('name')
    return None

if __name__ == '__main__':
    app.run(debug=True)

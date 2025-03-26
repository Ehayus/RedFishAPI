import requests
import json

# Load PDU IPs from JSON file
with open("filtered_pdu_ips.json", "r") as file:
    pdu_ips = json.load(file)["pdu_ips"]

# Load SNMP configuration from JSON file
with open("snmp_config.json", "r") as file:
    payload = json.load(file)

# Credentials (change accordingly)
USERNAME = "admin"
PASSWORD = "password"

# Headers for Redfish API
HEADERS = {
    "Content-Type": "application/json",
    "OData-Version": "4.0"
}

# Loop through each PDU and enable SNMP
for ip in pdu_ips:
    url = f"https://{ip}/redfish/v1/Managers/BMC/NetworkProtocol"
    try:
        response = requests.patch(url, headers=HEADERS, json=payload, auth=(USERNAME, PASSWORD), verify=False)
        if response.status_code == 200:
            print(f"[✅] SNMP enabled successfully on {ip}")
        else:
            print(f"[❌] Failed on {ip}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[⚠️] Error on {ip}: {e}")
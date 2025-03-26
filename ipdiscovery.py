import socket
import requests
import json

# Credentials (change accordingly)
USERNAME = "admin"
PASSWORD = "password"

# Headers for Redfish API
HEADERS = {
    "Content-Type": "application/json",
    "OData-Version": "4.0"
}

def discover_pdu_ips(subnet):
    pdu_ips = []
    for i in range(1, 255):  # Scan the last octet of the subnet
        ip = f"{subnet}.{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)  # Set a timeout for the connection
                if s.connect_ex((ip, 443)) == 0:  # Check if port 443 is open
                    pdu_ips.append(ip)
                    print(f"Discovered device at {ip}")
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    return pdu_ips

def is_pdu(ip):
    """
    Check if the device at the given IP is a PDU by querying its Redfish API.
    """
    try:
        # Query the Redfish root endpoint
        url = f"https://{ip}/redfish/v1"
        response = requests.get(url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)

        if response.status_code == 200:
            data = response.json()
            print(f"Redfish response from {ip}: {json.dumps(data, indent=4)}")  # Debugging

            # Check for the presence of the PowerEquipment field
            if "PowerEquipment" in data:
                return True
    except Exception as e:
        print(f"[⚠️] Error checking device at {ip}: {e}")
    return False

# Define the subnet to scan (e.g., 192.168.1)
subnet = "192.168.1"

# Discover devices with port 443 open
pdu_ips = discover_pdu_ips(subnet)

# Save the discovered IPs to a JSON file
with open("allip.json", "w") as file:
    json.dump({"pdu_ips": pdu_ips}, file)

print("Discovered devices:", pdu_ips)
print("Device IPs saved to allip.json")

# Filter out non-PDU devices
filtered_pdu_ips = [ip for ip in pdu_ips if is_pdu(ip)]

print("Filtered PDU IPs:", filtered_pdu_ips)

# Save the filtered PDU IPs to a new JSON file
with open("filtered_pdu_ips.json", "w") as file:
    json.dump({"pdu_ips": filtered_pdu_ips}, file)

print("Filtered PDU IPs saved to filtered_pdu_ips.json")
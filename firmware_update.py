#!/usr/bin/python3
# SPDX-License-Identifier: BSD-3-Clause
#Usage: python firmware_update.py 192.168.1.130 --user admin --passwd password --disable-cert-check
import argparse, logging, requests, sys, time
import sushy

parser = argparse.ArgumentParser(sys.argv[0], description="Redfish PDU Firmware Update")
parser.add_argument("ip", type=str, help="IP address of PDU")
parser.add_argument("--user", type=str, help="Username", default="admin")
parser.add_argument("--passwd", type=str, help="Password", default="legrand")
parser.add_argument("--cert", type=str, help="Server certificate")
parser.add_argument("--disable-cert-check", action="store_true", help="Disable certificate check")
args = parser.parse_args()

# Hardcoded firmware URL (Modify this as needed)
FIRMWARE_URL = "https://cdn1.raritan.com/download/pdu-g4/4.2.10/pdug4_ixg4_combined_4.2.10_50400.zip"

if args.disable_cert_check:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Set log level
LOG = logging.getLogger("sushy")
LOG.setLevel(logging.WARNING)
LOG.addHandler(logging.StreamHandler())

# Authentication
auth = sushy.auth.BasicAuth(username=args.user, password=args.passwd)
try:
    root = sushy.Sushy(f"https://{args.ip}/redfish/v1", auth=auth, verify=args.cert or not args.disable_cert_check)
except sushy.exceptions.ConnectionError as e:
    print(e)
    if "CERTIFICATE_VERIFY_FAILED" in str(e):
        print("\nYou should download 'Active TLS Certificate' from PDU and pass it using option")
        print("   --cert active_cert.pem")
        print("Alternatively, you may disable certificate check using option")
        print("   --disable-cert-check\n")
    exit()

# Get firmware version
mgr_inst = root.get_manager()
print("Current Firmware Version:", mgr_inst.firmware_version)

# Define Manager and firmware update URLs
manager_url = f"https://192.168.1.130/redfish/v1/Managers"
firmware_update_url = None;

# Search for firmware update URL under Manager
response = requests.get(manager_url, auth=(args.user, args.passwd), verify=False)

if response.status_code == 200:
    manager_data = response.json()
    # Print available manager details
    print("Manager Details:", manager_data)

    # Check if there's a firmware update action
    if "Actions" in manager_data and "UpdateFirmware" in manager_data["Actions"]:
        firmware_update_url = manager_data["Actions"]["UpdateFirmware"]
else:
    print(f"❌ Failed to retrieve Manager data. Status Code: {response.status_code}")
    print("Response:", response.text)
    exit()

# Function to trigger firmware update
def trigger_firmware_update():
    if not firmware_update_url:
        print("❌ No firmware update URL found.")
        return None

    payload = {"ImageURI": FIRMWARE_URL}
    response = requests.post(firmware_update_url, json=payload, auth=(args.user, args.passwd), verify=False)

    if response.status_code == 202:
        print("✅ Firmware update started successfully.")
        task_url = response.headers.get("Location")
        print(f"Monitor task at: {task_url}")
        return task_url
    else:
        print(f"❌ Firmware update failed! Status Code: {response.status_code}")
        print("Response:", response.text)
        return None

# Function to monitor update progress
def monitor_update(task_url):
    while True:
        response = requests.get(task_url, auth=(args.user, args.passwd), verify=False)

        if response.status_code == 200:
            task_data = response.json()
            task_state = task_data.get("TaskState")
            print(f"Update Status: {task_state}")

            if task_state in ["Completed", "Exception"]:
                print("✅ Firmware update finished with state:", task_state)
                break
        else:
            print(f"❌ Error monitoring update. Status Code: {response.status_code}")
            print("Response:", response.text)
            break

        time.sleep(5)  # Wait before checking again

# Run firmware update
task_url = trigger_firmware_update()
if task_url:
    monitor_update(task_url)

auth.close()

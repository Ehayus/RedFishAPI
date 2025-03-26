#!/usr/bin/python3
# SPDX-License-Identifier: BSD-3-Clause
#python redfish-example.py 192.168.1.130 --user admin --passwd password --disable-cert-check 
# Copyright 2022 Raritan Inc. All rights reserved.

import argparse, logging, requests, sys

import sushy
from sushy.resources import common, base

# As long as sushy does not provide specialized classes for PowerEquipment,
# generic classes UniversalResource and UniversalCollection may be used.
from universal_resources import get_collection, get_resource

parser = argparse.ArgumentParser(sys.argv[0], description = "Redfish example")
parser.add_argument('ip', type=str, help='ip address')
parser.add_argument('--user', type=str, help='user name', default="admin")
parser.add_argument('--passwd', type=str, help='password', default="legrand")
parser.add_argument('--cert', type=str, help='server certificate')
parser.add_argument('--disable-cert-check', action='store_true', help='disable certificate check')
args = parser.parse_args()

if args.disable_cert_check:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Set log level
LOG = logging.getLogger('sushy')
LOG.setLevel(logging.WARNING)
LOG.addHandler(logging.StreamHandler())

# Available authentication methods are:
#    auth = sushy.auth.BasicAuth(username=args.user, password=args.passwd)
#    auth = sushy.auth.SessionAuth(username=args.user, password=args.passwd)
#    auth = sushy.auth.SessionOrBasicAuth(username=args.user, password=args.passwd)
#
# Session authentification using "SessionAuth" or "SessionOrBasicAuth" may lead to an error
# message "Authentication error detected. Cannot proceed: HTTP ... returned code 401".
# At least in python3-sushy-3.7.0-4 this might not have any impact to the following
# operations. Reason is that SessionService wants to access to `/redfish/v1/SessionService`
# without authentication. This is forbidden, see DSP0266 "15.3.2 Authentication requirements"
auth = sushy.auth.BasicAuth(username=args.user, password=args.passwd)
try:
    root = sushy.Sushy(f'https://{args.ip}/redfish/v1', auth = auth, verify=args.cert or not args.disable_cert_check)
except (sushy.exceptions.ConnectionError) as e:
    print(e)
    if "CERTIFICATE_VERIFY_FAILED" in str(e):
        print()
        print("You should download 'Active TLS Certificate' from PDU and pass it using option")
        print("   --cert active_cert.pem")
        print("Alternatively you may disable certificate check using option")
        print("   --disable-cert-check")
        print()
    exit()

# get firware version from the single manager
mgr_inst = root.get_manager()
print("Firmware Version: ", mgr_inst.firmware_version)

# As long as sushy does not provide specialized classes for PowerEquipment,
# generic classes UniversalResource and UniversalCollection may be used.
# The required specific properties are defined as "fields" parameters
# and passed to these classes or get_resource() / get_collection() / get_member() / get_members()
power_fields = {
    "name": base.Field('Name'),
    "status": base.Field('Status'),
    "rack_pdus": common.IdRefField('RackPDUs'),
}
power_equipment = get_resource(root, '/redfish/v1/PowerEquipment', fields = power_fields)
print("PowerEquipment")
print("  Name:           ", power_equipment.name)
print("  Status.Health:  ", power_equipment.status["Health"])

rack_pdus = get_collection(root, power_equipment.rack_pdus.resource_uri)
print("  RackPDUs:")
print("    Name:         ", rack_pdus.name)
print("    Members:      ", len(rack_pdus.get_members()))

pdu_fields = {
    "id": base.Field('Id'),
    "manufacturer": base.Field('Manufacturer'),
    "model": base.Field('Model'),
    "serial": base.Field('SerialNumber'),
    "mains": common.IdRefField('Mains'),
    "outlets": common.IdRefField('Outlets'),
    "sensors": common.IdRefField('Sensors'),
}
for pdu in rack_pdus.get_members(pdu_fields):
    print("    PDU", pdu.id)
    print("      Manufacturer: ", pdu.manufacturer)
    print("      Model       : ", pdu.model)
    print("      Serial      : ", pdu.serial)

    if (pdu.mains):
        mains = get_collection(root, pdu.mains.resource_uri)
        print("      Mains:")
        print("        Name:     ", mains.name)
        print("        Members:  ", len(mains.get_members()))

        main_fields = {
            "id": base.Field('Id'),
            "voltage": base.Field(['Voltage', 'Reading']),
            "power": base.Field(['PowerWatts', 'Reading']),
        }
        for main in mains.get_members(main_fields):
            print("        Main", main.id)
            print("          Voltage: ", main.voltage, "V")
            print("          Power:   ", main.power, "W")

    if (pdu.outlets):
        outlets = get_collection(root, pdu.outlets.resource_uri)
        print("      Outlets:")
        print("        Name:     ", outlets.name)
        print("        Members:  ", len(outlets.get_members()))

        outlet_fields = {
            "id": base.Field('Id'),
            "voltage": base.Field(['Voltage', 'Reading']),
            "power": base.Field(['PowerWatts', 'Reading']),
            "state": base.Field(['PowerState']),
            "switch": base.Field(['Actions', '#Outlet.PowerControl', 'target']),
        }
        for outlet in outlets.get_members(outlet_fields):
            print("        Outlets", outlet.id)
            print("          Voltage: ", outlet.voltage, "V")
            print("          Power:   ", outlet.power, "W")
            if (outlet.switch):
                print("          State:   ", outlet.state)
                new_state = "Off" if outlet.state == "On" else "On"
                print("          >>> Switch to", new_state)
                root._conn.post(outlet.switch, data={'PowerState': new_state})

    if (pdu.sensors):
        sensors = get_collection(root, pdu.sensors.resource_uri)
        print("      Sensors:")
        print("        Name:     ", sensors.name)
        print("        Members:  ", len(sensors.get_members()))

        sensor_fields = {
            "id": base.Field('Id'),
            "reading": base.Field('Reading'),
        }
        for sensor in sensors.get_members(sensor_fields):
            print("        Sensor", sensor.id)
            print("          Reading: ", sensor.reading)


auth.close()

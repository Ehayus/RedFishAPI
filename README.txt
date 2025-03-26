HOWTO for Redfish interface
---------------------------

1) Supported Service for Redfish version v1

    - AccountService    : provides account and permission management
    - CertificateService: provides HTTPS server certificate management
    - SessionService    : allows session based authentication
    - Managers          : provides access to basic system configuration (firmware, network configuration)
    - PowerEquipment    : contains everything that concerns measuring and switching of electricity

  PowerEquipment supports per PDU:

    - Metrics      : total power and energy readings
    - Mains        : states and measurements for inlets
    - Outlets      : states, measurements and actions for outlets
    - OutletGroups : states, measurements and actions for outlet groups
    - Branches     : states and measurements for OCPs
    - Sensors      : states and measurements for external Sensors

2) How to start

  First, make sure the Redfish service is enabled. Login to Web-GUI, navigate to
  "Device Settings" -> "Network Services" -> "Redfish". The checkbox
  "Enable Redfish Service" must be checked.

  The following assumes you have a PDU with switchable outlets that is reachable
  via IP address 10.0.42.2, and the default credentials admin/legrand are active.

3) Use curl to get first access

  You may use "curl" to read JSON from https://10.0.42.2/redfish and subtrees. For the
  root path and some exceptions there is no authentication required. Otherwise, pass
  the credentials in the URI. To make the JSON response clearer, "jq" can be used, in
  conjunction with options "-f -s -S".

  Per default, the usage of HTTPS requires a valid server certificate signed by a CA
  known to the Operating System. As alternative, you can disable the security check
  using option "-k".


    (a) Read Redfish root, see available versions

      curl -kfsS https://10.0.42.2/redfish

    (b) Read Redfish version v1 service root

      curl -kfsS https://10.0.42.2/redfish/v1 | jq

      The service root shows all supported services. Currently there are:

        - AccountService
        - CertificateService
        - SessionService
        - Managers
        - PowerEquipment

      For each service and sub-items there are links in "@odata.id" you can follow.

    (c) Follow PowerEquipment -> RackPDUs -> first Members entry

        Authentication is now required.

        curl -kfsS https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment | jq
        curl -kfsS https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment/RackPDUs | jq
        curl -kfsS https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment/RackPDUs/1 | jq

        This is PDU root. From here there are links to:

          - Metrics
          - Mains
          - Outlets
          - OutletGroups
          - Branches
          - Sensors

    (d) Follow Outlets ->  first Members entry

        curl -kfsS https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment/RackPDUs/1/Outlets | jq
        curl -kfsS https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment/RackPDUs/1/Outlets/1 | jq

        Here you can see all measured values and states for the outlet. In addition, there is a
        reference to the outlet switch in Actions.

    (e) Switch outlet power (follow Actions.#Outlet.PowerControl.target)

        curl -kfsS -d '{"PowerState" : "Off"}' https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment/RackPDUs/1/Outlets/1/Actions/Outlet.PowerControl
        curl -kfsS -d '{"PowerState" : "On"}' https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment/RackPDUs/1/Outlets/1/Actions/Outlet.PowerControl

    (f) Change oulet label

        curl -kfsS -X PATCH -d '{"UserLabel":"My Outlet"}' https://admin:legrand@10.0.42.2/redfish/v1/PowerEquipment/RackPDUs/1/Outlets/1 | jq


4) Try out python example

    (a) The attached "redfish-example.py" requires the Python library "sushy".

        - Install "sushy" on Fedora

            sudo dnf install python3-sushy

        - Otherwise

            pip install sushy

    (b) Run "redfish-example.py"

        Per default, the usage of HTTPS requires a valid server certificate signed by a CA
        known to the Operating System. To disable the certificate check for testing, use
        "--disable-cert-check".

           ./redfish-example.py 10.0.42.2 --disable-cert-check

        For further options, especially in case of non-default credentials, use:

           ./redfish-example.py --help

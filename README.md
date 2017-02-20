# network_config

Utility to configure network interfaces in Linux environment.
The following input parameters are read from user and network 
interface and route are configured.

Parameters:

      - ifname  - Name of the network interface
      - address - IP address to configure on the network interface
      - network - Network address with network prefix
      - gateway - Gateway IP address (IPv6)
      - mtu     - MTU size to be set on the interface

Validation:

      Input parametes are validated as follows:
      - ifname - is checked for empty string
      - address - the ip address is validate for:
                             - IPv6
                             - address must be in the given network
      - network - network address is checked for IPv6
      - gateway - gateway address is checked for IPv6.
     - mtu 

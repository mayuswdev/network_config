# network_config

Utility to configure network interfaces in Linux environment.
The following input parameters are read from user and network 
interface and route are configured.

###Parameters:

      - ifname  - Name of the network interface
      - address - IP address to configure on the network interface
      - network - Network address with network prefix
      - gateway - Gateway IP address (IPv6)
      - mtu     - MTU size to be set on the interface

###Validation:

      Input parametes are validated as follows:
      - ifname - is checked for empty string
      - address - the ip address is validate for:
                             - IPv6
                             - address must be in the given network
      - network - network address is checked for IPv6
      - gateway - gateway address is checked for IPv6.
      - mtu     - mtu size must be between 1028 and 65336 bytes


##Help
```
$ python3 network_config.py -h
usage: network_config.py [-h] [-v] [-s] [-i IFNAME] [-a ADDRESS] [-n NETWORK]
                         [-g GATEWAY] [-m MTU]

Utility to configure network parameters on an interface

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode to print debug traces
  -s, --silent          silent execution (no prompt for confirmation)
  -i IFNAME, --ifname IFNAME
                        network interface name
  -a ADDRESS, --address ADDRESS
                        IPv6 address to be set
  -n NETWORK, --network NETWORK
                        IPv6 network address i.e: 2001:0DB8:1:0/48
  -g GATEWAY, --gateway GATEWAY
                        IPv6 gateway ip address
  -m MTU, --mtu MTU     mtu size, between 1028 and 65336 bytes
```

###Logs 
Logs are written to /var/log/network_config.log file.

###Example 1 - parameters are specified in command line
```
$ sudo python3 network_config.py  -i enp0s9  -a 2001:2002::11 -n 2001:2002::/64 -g 2001:2002::1 -m 9000

The following network parameters will be configured on interface: enp0s9
IP Address  : 2001:2002::11
Network     : 2001:2002::/64    Prefixlen: 64
Gateway IP  : 2001:2002::1
MTU         : 9000
Please confirm to continue: (Y/N):Y
Network parameters successfully configured for interface: enp0s9
Route successfully added network: 2001:2002::/64, gateway: 2001:2002::1

```

###Example 2 
```
$ sudo python3 network_config.py
Enter network interface name: enp0s8
Enter IPv6 address          : 2001:2002::101
Enter IPv6 network (address/prefixlen): 2001:2002::/64
Enter IPv6 gateway address  : 2001:2002::1
Enter MTU size              : 9000

The following network parameters will be configured on interface: enp0s8
IP Address  : 2001:2002::101
Network     : 2001:2002::/64    Prefixlen: 64
Gateway IP  : 2001:2002::1
MTU         : 9000
Please confirm to continue: (Y/N):Y
Network parameters successfully configured for interface: enp0s8
Route successfully added network: 2001:2002::/64, gateway: 2001:2002::1
```

###Example 3 - network and ip address validation (error case)
```
$ sudo python3 network_config.py  
Enter network interface name: enp0s8
Enter IPv6 address          : 2001:2002::101
Enter IPv6 network (address/prefixlen): 2001:2003::/64
Enter IPv6 gateway address  : 2001:2002::1
Enter MTU size              : 9000
IPv6 Address: 2001:2002::1 is not in Network: 2001:2003::/64
```

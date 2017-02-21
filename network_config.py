"""network_config.py:  Utility to configure network interfaces on Linux environment.

   Author: Mayuran Subramaniam
   Email : mayuran.sub@gmail.com


    The following input parameters are read from user and network interface and route are configured.

    Parameters:
      - ifname  - Name of the network interface
      - address - IP address to configure on the network interface
      - network - Network address with network prefix
      - gateway - Gateway IP address (IPv6)
      - mtu     - MTU size to be set on the interface

    Validation:
      The following parameters are validated:
        - ifname - is checked for empty string
        - address - the ip address is validate for:
                             - IPv6
                             - address must be in the given network
        - network - network address is checked for IPv6
        - gateway - gateway address is checked for IPv6.
        - mtu - MTU size must be between 1280 bytes (IPv6 minimum) and 65536 bytes.
"""


import sys
import os
import subprocess
import shlex
import ipaddress
from argparse import ArgumentParser
import logging


C_RED = '\033[0;31m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[0;33m'
C_NO_COLOR = '\033[0m'
C_BLUE = '\033[94m'
C_BOLD = '\033[1m'


logger = None

def init_log():
   global logger
   logging.basicConfig(level=logging.DEBUG,
                       format='%(asctime)s - %(name)-10s %(levelname)-10s %(message)s',
                       datefmt='%m-%d %H:%M:%S',
                       filename='/var/log/network_config.log',
                       filemode='a')

   ch = logging.StreamHandler()
   ch.setLevel(logging.DEBUG)
   formatter = logging.Formatter('%(message)s')
   ch.setFormatter(formatter)

   logger = logging.getLogger('network_config')
   logger.addHandler(ch)


def exit_now(code):
   logging.shutdown()
   sys.exit(code)

    
def print_info(message):
   if logger:
       logger.info("{0:s}".format(message))
   else:
       print("{0:s}".format(message))


def print_warn(message):
   if logger:
      logger.warn("{0:s}{1:s}{2:s}".format(C_YELLOW,message,C_NO_COLOR))
   else:
      print("{0:s}WARNING: {1:s}{2:s}".format(C_YELLOW,message,C_NO_COLOR))


def print_debug(message):
   if args.verbose:
      if logger:
         logger.debug("{0:s}".format(message))
      else:
         print("DEBUG: {0:s}".format(message))


def print_error(message, kill = True):
   if logger:
      logger.error("{0:s}{1:s}{2:s}".format(C_RED, message, C_NO_COLOR))
   else:
      print("{0:s}ERROR: {1:s}{2:s}".format(C_RED, message, C_NO_COLOR))

   if kill: 
      exit_now(1)


def run_os_command(command):
   print_debug(command)

   command_seq = shlex.split(command)
   proc = subprocess.Popen(command_seq, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   try:
      outs, errs = proc.communicate(timeout=30)
   except TimeoutExpired: 
      proc.kill()
      outs, errs = proc.communicate()

   return outs.decode('utf-8').strip(), errs.decode('utf-8').strip()


def is_valid_ifname(ifname):
   if not ifname or ifname == '':
      return False 
   return True


def is_valid_address(address):
   global cfg;

   if not address:
      return False

   try:
      ip = ipaddress.ip_address(address)
      if ip.version == 6:
         cfg['ipv6address'] = ip
         return True
      else:
         print_warn("Not an IPv6 address...")
   except ValueError as error:
      print_warn(str(error))

   return False


def is_valid_network(network):
   global cfg
   if not network: 
      return False

   try:
      net = ipaddress.ip_network(network)
      if (net.version == 6):
         cfg['ipv6network'] = net
         cfg['prefixlen'] = str(net.prefixlen)
         return True
      else:
         print_warn("Not an IPv6 Network address...")
   except ValueError as error:
      print_warn(str(error))

   return False


def is_valid_mtu(mtu):
   if not mtu:
      return False

   try:
      value = int(mtu)
      if value >= 1280 and value <= 65536:
         return True
      else:
         print_info("MTU size  must be between 1280 and 65536 bytes")
   except ValueError:
      pass

   return False


def config_network(cfg):
   ifconfig_command  = ("ifconfig {0:s} inet6 add {1:s}/{2:s} mtu {3:s}"
                       .format(cfg['ifname'], cfg['address'], cfg['prefixlen'], cfg['mtu']))

   out,err = run_os_command(ifconfig_command)
   if err:
      print_error("Failed to configure network interface: {0:s}, error: '{1:s}'"
                  .format(cfg['ifname'], err))
   else:
      print_info("{0:s}Network parameters successfully configured for interface: {1:s}{2:s}"
                 .format(C_GREEN, cfg['ifname'], C_NO_COLOR)) 
 
   route_command = ("route -A inet6 add {0:s} gw {1:s}".format(cfg['network'], cfg['gateway']))
   out, err = run_os_command(route_command)   
   if err:
      print_error("Failed to add route for network: {0:s}, gw: {1:s}, error: '{2:s}'"
                  .format(cfg['network'], cfg['gateway'], err))
   else:
      print_info("{0:s}Route successfully added network: {1:s}, gateway: {2:s}{3:s}"
                  .format(C_GREEN, cfg['network'], cfg['gateway'], C_NO_COLOR))


def read_input(message, parameter, validate_function=None):
   value = input(message).strip()
   if validate_function:
      while True:
         if value == 'q' or value == 'quit':
            print_info("Quiting...")
            exit_now(0)

         if validate_function(value):
            return value
         else:
            print_info("Invalid value entered for {0:s}, try again...".format(parameter))
            value = input(message).strip()
   return value


def read_input_parameters(args, cfg):
   if args.ifname:
      cfg['ifname'] = args.ifname.strip()
   else:
      cfg['ifname'] = read_input("Enter network interface name: ", 'interface name', is_valid_ifname)
 
   if args.address:
      cfg['address'] = args.address
   if not is_valid_address(cfg['address']):
      cfg['address'] = read_input("Enter IPv6 address          : ", 'ip address', is_valid_address)
 
   if args.network:
      cfg['network'] = args.network
   if not is_valid_network(cfg['network']):
      cfg['network'] = read_input("Enter IPv6 network (address/prefixlen): ", 'network address', is_valid_network)

   if args.gateway:
      cfg['gateway'] = args.gateway
   if not is_valid_address(cfg['gateway']):
      cfg['gateway'] = read_input("Enter IPv6 gateway address  : ", 'gateway', is_valid_address)
         
   if args.mtu:
      cfg['mtu'] = args.mtu
   if not is_valid_mtu(cfg['mtu']):
      cfg['mtu'] = read_input("Enter MTU size              : ", 'mtu', is_valid_mtu)

   if not cfg['ipv6address'] in cfg['ipv6network']:
      print_error("IPv6 Address: {0:s} is not in Network: {1:s}"
                  .format(str(cfg['ipv6address']), str(cfg['ipv6network'])))

   print_info("\nThe following network parameters will be configured on interface: " +
              C_GREEN + cfg['ifname'] +
              "\nIP Address  : " + cfg['address'] + 
              "\nNetwork     : " + cfg['network'] + "    Prefixlen: " + cfg['prefixlen'] +
              "\nGateway IP  : " + cfg['gateway'] +
              "\nMTU         : " + cfg['mtu'] +
               C_NO_COLOR)

   if not args.silent:
      yn = input("{0:s}{1:s}Please confirm to continue: (Y/N):{2:s}".format(C_BOLD, C_GREEN, C_NO_COLOR))
      yn.strip()
      if 'N' in yn.upper() or 'Q' in yn.upper():
         print_warn("Exiting....")
         exit_now(0)


## MAIN ###
parser = ArgumentParser(description='Utility to configure network parameters on an interface')
#verbose
parser.add_argument('-v', '--verbose', help='verbose mode to print debug traces', action='store_true')
#silence
parser.add_argument('-s', '--silent', help='silent execution (no prompt for confirmation)', action='store_true')
#interface
parser.add_argument('-i', '--ifname',  help='network interface name', type=str)
#ip address
parser.add_argument('-a', '--address', help='IPv6 address to be set', type=str)
#net mask
parser.add_argument('-n', '--network', help='IPv6 network address i.e: 2001:0DB8:1:0/48', type=str)
#gateway ip
parser.add_argument('-g', '--gateway', help='IPv6 gateway ip address', type=str)
#mtu
parser.add_argument('-m', '--mtu', help='mtu size, between 1028 and 65336 bytes', type=str)


try:
   args = parser.parse_args()
   cfg = {}
   cfg['ifname'] = args.ifname 
   cfg['address'] = args.address
   cfg['ipv6address'] = None
   cfg['network'] = args.network
   cfg['ipv6network'] = None
   cfg['prefixlen'] = None
   cfg['gateway'] = args.gateway
   cfg['mtu'] = args.mtu

   try:
      init_log()
   except:
      print_warn('Cannot initialize logger, printing traces to the console!')

   read_input_parameters(args, cfg)
 
   config_network(cfg)
 
except KeyboardInterrupt:
   exit_now(1)

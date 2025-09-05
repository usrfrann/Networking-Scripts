from typing import List

from netmiko import ConnectHandler, ReadTimeout
import argparse
import getpass
import logging
import ast


HOST_LIST = ['<host>', '<host>']
INTERFACE_DICT = {'<host>': ['<Interface>', '<Interface>'], '<Host>': ['<Interface>', '<Interface>']}
USERNAME = '<username>'
PASSWORD = '<password>'
SECRET = '<secret>'


def main():
    DEVICE_TYPE = 'cisco_ios'
    parser = argparse.ArgumentParser(description=" Cisco Port Security Script")
    parser.add_argument("--username", type=str, help="username")
    parser.add_argument("--host_list", type=str, help="host_list eg: ['<host>', '<host>']")
    parser.add_argument("--interface_list", type=str, help="interface_list eg {'<host>': ['<Interface>', '<Interface>'], '<Host>': ['<Interface>', '<Interface>']}")
    args = parser.parse_args()

    username = args.username if args.username else input(f'Enter Username (default: {USERNAME}): ')
    host_list= args.host_list if args.host_list else input(f"""'Enter Host: eg['<host>', '<host>'] (default: {HOST_LIST}): '""")
    #List host
    interface_list = args.interface_list if args.interface_list else input(f"""Enter Interface Dict: (default: {INTERFACE_DICT}): """)
    if not username:
        username = USERNAME
    if not host_list:
        host_list = HOST_LIST
    if not interface_list:
        interface_list = INTERFACE_DICT

    password = getpass.getpass("Enter your Password:")
    secret = getpass.getpass("Enter your Secret:")
    if not password:
        password = PASSWORD
    if not secret:
        secret = SECRET
    print(args)
    host_list = ast.literal_eval(host_list)
    interface_list = ast.literal_eval(interface_list)
    for host in host_list:
        cisco_device = {
            'device_type': DEVICE_TYPE,
            'host': host,
            'username': username,
            'password': password,
            'secret': secret,
        }

        create_port_security(cisco_device, interface_list)


def create_port_security(cisco_device, interface_l):
    try:
        net_connect = ConnectHandler(**cisco_device)
        net_connect.enable()
        print(interface_l)
        for host, interfaces in interface_l.items():
            if (host.strip() == cisco_device['host'].strip()):
                for interface in interfaces:
                    port_security = [
                        f'int {interface} ',
                        f'switchport port-security ',
                        f'switchport port-security mac-address sticky ',
                        'exit'
                    ]
                    print(port_security)
                    output = net_connect.send_config_set(port_security)
                    save_output = net_connect.save_config()
                    logging.info(output)
    except Exception as e:
        logging.error(e)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
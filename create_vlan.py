from netmiko import ConnectHandler, ReadTimeout
import argparse
import getpass
import logging

def main():
    DEVICE_TYPE = 'cisco_ios'
    HOST = ''
    USERNAME = ''
    PASSWORD = ''
    SECRET = ''
    VLAN_ID = '<int>'
    VLAN_NAME = ''
    VLAN_INTERFACE_RANGE = "fa0/4 - 7"
    ACCESS_TYPE = "access"

    parser = argparse.ArgumentParser(description=" Cisco Ping Script")
    parser.add_argument("--username", type=str, help="username")
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--vlan_id", type=int, help="vlan-id")
    parser.add_argument("--vlan_name", type=str, help="vlan-name")
    parser.add_argument("--vlan_interface_range", type=str, help="vlan interface range")
    parser.add_argument("--interface_access_type", type=str, help="interface access type")
    parser.add_argument("--allowed_vlan", type=int, help="allowed vlan id")
    args = parser.parse_args()

    username = args.username if args.username else input(f'Enter Username (default: {USERNAME}): ')
    host = args.host if args.host else input(f'Enter Host (default: {HOST}): ')
    vlan_id = args.vlan_id if args.vlan_id else input(f'Enter VLAN ID (default: {VLAN_ID}): ')
    vlan_name = args.vlan_name if args.vlan_name else input(f'Enter VLAN name (default: {VLAN_NAME}): ')
    vlan_interface_range = args.vlan_interface_range if args.vlan_interface_range else input(f'Enter VLAN interface range (default: {VLAN_INTERFACE_RANGE}): ')
    interface_access_type = args.interface_access_type if args.interface_access_type else input(f'Enter interface access type (default: {ACCESS_TYPE}): ')
    allowed_vlans = None
    if interface_access_type == 'trunk':
        allowed_vlans = args.allowed_vlan if args.allowed_vlan else input(f'Enter allowed VLANs (default: {VLAN_ID}): ')
    if not username:
        username = USERNAME
    if not host:
        host = HOST
    if not vlan_id:
        vlan_id = VLAN_ID
    if not vlan_name:
        vlan_name = VLAN_NAME
    if not vlan_interface_range:
        vlan_interface_range = VLAN_INTERFACE_RANGE
    if not interface_access_type:
        interface_access_type = ACCESS_TYPE
    password = getpass.getpass("Enter your Password:")
    secret = getpass.getpass("Enter your Secret:")
    if not password:
        password = PASSWORD
    if not secret:
        secret = SECRET

    cisco_device = {
        'device_type': DEVICE_TYPE,
        'host': host,
        'username': username,
        'password': password,
        'secret': secret,
    }

    create_access_vlan(vlan_id, vlan_name, vlan_interface_range, cisco_device, interface_access_type, allowed_vlans)


def create_access_vlan(v_id, v_name, v_i_range, c_device, access_type, a_vlans):
    try:
        cisco_device = ConnectHandler(**c_device)
        cisco_device.enable()
        vlan_commands = [
            f'vlan {v_id}',
            f'name {v_name}',
            'exit'

        ]
        if access_type == 'access':
            switch_mode_option = f"switchport access vlan {v_id}"
        elif access_type == 'trunk':
            switch_mode_option = f"switchport truck allowed vlan {",".join(a_vlans.split())}"
        else:
            switch_mode_option = None

        interface_command = [
            f'interface range {v_i_range}',
            switch_mode_option,
            f'switchport mode {access_type}',
            'end'
        ]
        #print(interface_command)
        output = cisco_device.send_config_set(vlan_commands)
        output_2 = cisco_device.send_config_set(interface_command)
        save_output = cisco_device.save_config()
        #isco_device.disconnect()
        logging.info(output)
        logging.info(save_output)
    except Exception as e:
        logging.error(f'Exception {e}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
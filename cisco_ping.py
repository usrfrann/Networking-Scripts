from netmiko import ConnectHandler, ReadTimeout
import argparse
import getpass
# Extracted constants for better organization and security

def main():
    DEVICE_TYPE = 'cisco_ios_telnet'
    HOST = '<ip>'
    USERNAME = '<username>'
    PASSWORD = '<password>'
    PING_LIST = '[<ping_list>]'


    parser = argparse.ArgumentParser(description=" Cisco Ping Script")
    parser.add_argument("--username", type=str, help="username")
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--ping_list", type=str, help="list of devices to ping, please enclose in quotes and comma seprated eg: ('0.0.0.0, 1.1.1.1')")
    args = parser.parse_args()

    username = args.username if args.username else input(f'Enter Username (default: {USERNAME}): ')
    host = args.host if args.host else input(f'Enter Host (default: {HOST}): ')
    if not username:
        username = USERNAME
    if not host:
        host = HOST

    if args.ping_list:
        ping_list = args.ping_list.split(',')
    else:
        ping_list = input(f"Enter list of devices to ping, please enclose in quotes and comma seprated eg: ('0.0.0.0, 1.1.1.1')")
        if ping_list:
            ping_list = ping_list.split(',')
        else:
            ping_list = PING_LIST
    password = getpass.getpass("Enter your Password:")
    if not password:
        password = PASSWORD

    cisco_device = {
        'device_type': DEVICE_TYPE,
        'host': host,
        'username': username,
        'password': password,
    }
    cisco_device = ConnectHandler(**cisco_device)
    for ping_target in ping_list:
        ping_command = f'ping {ping_target}'
        try:
            ping_output = cisco_device.send_command(ping_command)
            print(f"Ping result for {ping_target}: \n {ping_output}")
        except ReadTimeout:
            print(f"Ping failed for {ping_target}")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
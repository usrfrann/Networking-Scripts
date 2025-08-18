from netmiko import ConnectHandler, ReadTimeout
import argparse
import getpass

def main():
    DEVICE_TYPE = 'cisco_ios'
    HOST = ''
    USERNAME = ''
    PASSWORD = ''
    SECRET = ''



    parser = argparse.ArgumentParser(description=" Cisco Ping Script")
    parser.add_argument("--username", type=str, help="username")
    parser.add_argument("--host", type=str, help="host")
    args = parser.parse_args()

    username = args.username if args.username else input(f'Enter Username (default: {USERNAME}): ')
    host = args.host if args.host else input(f'Enter Host (default: {HOST}): ')
    if not username:
        username = USERNAME
    if not host:
        host = HOST

    password = getpass.getpass("Enter your Password:")
    secret = getpass.getpass("Enter your Secret:")
    if not password:
        password = PASSWORD
    if not secret:
        secret = SECRET
    try:
        cisco_device = {
            'device_type': DEVICE_TYPE,
            'host': host,
            'username': username,
            'password': password,
            'secret': secret,
        }
        cisco_device = ConnectHandler(**cisco_device)
        cisco_device.enable()
        commands = [
            "configure terminal",
            "event manager applet persist-debug",
            " event syslog pattern \"SYS-5-RESTART\"",
            " action 1.0 cli command \"enable\"",
            " action 1.1 cli command \"debug ip icmp\"",
            " action 1.2 cli command \"terminal monitor\"",
            "end"
        ]

        output = cisco_device.send_config_set(commands)
        save_output = cisco_device.save_config()
        cisco_device.disconnect()
        print(output)
        print(save_output)
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()
from netmiko import ConnectHandler, ReadTimeout
import argparse
import getpass

def main():
    DEVICE_TYPE = 'cisco_ios'
    HOST = ''
    USERNAME = ''
    PASSWORD = ''
    SECRET = ''
    AAAHOST = ''
    AAASECRET = ''


    parser = argparse.ArgumentParser(description=" Cisco Ping Script")
    parser.add_argument("--username", type=str, help="username")
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--aaa_host", type=str, help="aaa host")
    parser.add_argument("--aaa_secret", type=str, help="aaa secret")
    args = parser.parse_args()

    username = args.username if args.username else input(f'Enter Username (default: {USERNAME}): ')
    host = args.host if args.host else input(f'Enter Host (default: {HOST}): ')
    aaa_host = args.aaa_host if args.aaa_host else input(f'Enter AAA Host (default: {AAAHOST}): ')
    aaa_secret = args.aaa_secret if args.aaa_secret else input(f'Enter AAA Secret (default: {AAASECRET}): ')
    if not username:
        username = USERNAME
    if not host:
        host = HOST
    if not aaa_host:
        aaa_host = AAAHOST
    if not aaa_secret:
        aaa_secret = AAASECRET


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
    cisco_device = ConnectHandler(**cisco_device)
    cisco_device.enable()
    aaa_commands = [
        'aaa new-model ',
        f'radius-server host {aaa_host} auth-port 1812 acct-port 1813 key {aaa_secret} ',
        'aaa authentication login default group radius local ',
        'aaa authorization exec default group radius local ',
        'aaa accounting exec default start-stop group radius ',
        'aaa accounting commands 15 default start-stop group radius ',
        'line con 0 ',
        'login authentication default ',
        'line vty 0 15 ',
        'login authentication default '
    ]

    output = cisco_device.send_config_set(aaa_commands)
    save_output = cisco_device.save_config()
    cisco_device.disconnect()
    print(output)
    print(save_output)

if __name__ == '__main__':
    main()
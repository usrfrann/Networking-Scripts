from netmiko import ConnectHandler, ReadTimeout
import argparse
import getpass

def main():
    DEVICE_TYPE = 'cisco_ios'
    HOST = ''
    USERNAME = ''
    PASSWORD = ''
    SECRET = ''
    USERTOADD = ''


    parser = argparse.ArgumentParser(description=" Cisco Ping Script")
    parser.add_argument("--username", type=str, help="username")
    parser.add_argument("--host", type=str, help="host")
    parser.add_argument("--user_to_add", type=str, help="username to add to cisco device")
    parser.add_argument("--password_to_add", type=str, help="username to add to cisco device")
    args = parser.parse_args()

    username = args.username if args.username else input(f'Enter Username (default: {USERNAME}): ')
    host = args.host if args.host else input(f'Enter Host (default: {HOST}): ')
    user_to_add = args.user_to_add if args.user_to_add else input(f'Enter User to Add (default: {USERTOADD}): ')
    password_to_add = args.password_to_add if args.password_to_add else input(f'Enter Password to Add for NewUser (default: {PASSWORD}): ')
    if not username:
        username = USERNAME
    if not host:
        host = HOST
    if not user_to_add:
        user_to_add = USERTOADD
    if not password_to_add:
        password_to_add = PASSWORD

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
    create_user_commands = [
        f"username {user_to_add} privilege 15 secret {password_to_add}",
    ]
    enable_user_only = [
        'line vty 0 4',
        'transport input ssh',
    ]

    output = cisco_device.send_config_set(create_user_commands)
    output_2 = cisco_device.send_config_set(enable_user_only)
    save_output = cisco_device.save_config()
    cisco_device.disconnect()
    print(output)
    print(output_2)
    print(save_output)

if __name__ == '__main__':
    main()